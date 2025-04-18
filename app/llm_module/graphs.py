import datetime
import logging
import langgraph
from langgraph.graph import StateGraph, START, END
from app.llm_module.states import GenerationState, MainState, generation, main
from app.llm_module.agents import Verifier, Clarifier, X6Processor, Editor
from typing import Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenerationGraph:

    def __init__(self):
        self.graph = StateGraph(GenerationState)

        self._build_graph()

    def _build_graph(self):

        self.graph.add_node("verifier", self.verifier_node)
        self.graph.add_node("clarifier", self.clarifier_node)
        self.graph.add_node("x6processor", self.x6processor_node)
        self.graph.add_node("editor", self.editor_node)
        self.graph.add_node("bpmn_condition", self.bpmn_condition_node)

        self.graph.add_conditional_edges(START, self.entry_condition,
                                         {
                                                "verifier": "verifier",
                                             "clarifier": "clarifier",
                                                "bpmn_condition": "bpmn_condition"
                                         })

        self.graph.add_edge("x6processor", END)
        self.graph.add_edge("editor", END)

        self.graph.add_conditional_edges("verifier", self.verifier_condition,
                                         {
                                                "clarifier": "clarifier",
                                                END: END
                                         })

        self.graph.add_conditional_edges("clarifier", self.clarifier_condition,
                                         {
                                                "user_input_exit": END,
                                                "bpmn_condition": "bpmn_condition"
                                         })
        self.graph.add_conditional_edges("bpmn_condition", self.bpmn_condition, {
                                                "editor": "editor",
                                                "x6processor": "x6processor"
                                         })


    def __call__(self, state: GenerationState) -> GenerationState:
        logger.info(f"Processing state: {state}")
        graph = self.compile()
        state = graph.invoke(state)
        logger.info(f"State after processing: {state}")
        return state


    def compile(self):
        logger.info("Compiling the graph")
        graph = self.graph.compile()
        logger.info("Graph compiled")
        return graph

    @staticmethod
    def entry_condition(state: GenerationState) -> str:
        logger.info("Entry condition check")
        current = state["current"][1]
        if current in ["x6processor", "editor"]:
            logger.info("Entry condition met for bpmn condition")
            return "bpmn_condition"
        logger.info(f"Entry condition met for {current}")
        return current

    @staticmethod
    def verifier_node(state: GenerationState):
        state["current"] = ["generator", "verifier"]
        logger.info("Verifier agent is processing")
        verifier = Verifier(context=state["context"])
        state = verifier(state)
        logger.info("Verifier agent process ended")
        return state

    @staticmethod
    def verifier_condition(state: GenerationState) -> str:
        logger.info("Verifier agent condition check")
        if state["agents_result"]["verifier"]["result"].get("is_bpmn_request"):
            return "clarifier"
        return END

    @staticmethod
    def clarifier_node(state: GenerationState):
        state["current"] = ["generator", "clarifier"]
        logger.info("Clarifier agent is processing")
        if state["clarification_num_iterations"] <= 0:
            state["current"] = ["generator", "x6processor"]
            return state
        clarifier = Clarifier(context=state["context"])
        state = clarifier(state)
        state["clarification_num_iterations"] -= 1
        logger.info("Clarifier agent process ended")
        return state

    @staticmethod
    def clarifier_condition(state: GenerationState) -> str:
        logger.info("Clarifier agent condition check")
        if state["await_user_input"]:
            logger.info("User input exit condition met")
            return "user_input_exit"
        if state["clarification_num_iterations"] <= 0:
            logger.info("Clarification iterations ended")
            return "bpmn_condition"

    @staticmethod
    def x6processor_node(state: GenerationState):
        state["current"] = ["generator", "x6processor"]
        logger.info("X6Processor agent is processing")
        x6processor = X6Processor(context=state["context"])
        state = x6processor(state)
        state["bpmn"] = state["agents_result"]["x6processor"]["result"]
        logger.info("X6Processor agent process ended")
        return state

    @staticmethod
    def editor_node(state: GenerationState):
        state["current"] = ["generator", "editor"]
        logger.info("Editor agent is processing")
        editor = Editor(context=state["context"])
        state = editor(state)
        state["bpmn"] = state["agents_result"]["editor"]["result"]
        logger.info("Editor agent process ended")
        return state

    @staticmethod
    def bpmn_condition_node(state: GenerationState):
        return state

    @staticmethod
    def bpmn_condition(state: GenerationState) -> str:
        logger.info("Generation agent check")
        if state["bpmn"] != {"nodes": [], "edges": []}:
            logger.info("BPMN is present")
            return "editor"
        logger.info("BPMN is not present")
        return "x6processor"

query = ("Сделай мне диаграмму BPMN для процесса найма сотрудников. "
         "Я хочу, чтобы она была простой и понятной. "
         "Сделай так, чтобы она была на русском языке. "
         "И добавь туда все необходимые элементы. "
         "Список элементов: "
         "1. Начало процесса\n"
         "2. Сбор резюме\n"
         "3. Проведение собеседования\n"
         "4. Выбор кандидата\n"
         "5. Проверка рекомендаций\n"
         "6. Отправка предложения кандидату\n"
         "7. Подписание контракта\n"
         "8. Начало работы кандидата\n"
         "9. Завершение процесса\n")

state = generation(
    user_input=query,
)

graph = GenerationGraph()

state = graph(state)

state["user_input"] = "Добавь в нее еще 5 элементов по теме диаграммы"
state["await_user_input"] = False
state = graph(state)

print(state["bpmn"])

state["user_input"] = "БОТ уничтожь диаграмму"
state["await_user_input"] = False

state = graph(state)

print(state["bpmn"])

state["user_input"] = "Бот верни диаграмму но на корейском языке"

state["await_user_input"] = False

state = graph(state)

print(state["bpmn"])

from app.llm_module.test import visualize_bpmn_graph
from app.llm_module.src.markup_to_x6 import x6_layout

visualize_bpmn_graph(x6_layout(state["bpmn"]))