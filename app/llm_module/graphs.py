import logging
from langgraph.graph import StateGraph, START, END
from app.llm_module.states import GenerationState
from app.llm_module.agents import Verifier, Clarifier, X6Processor, Editor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenerationGraph:

    def __init__(self):
        """
        В графе используются состояния с фикс. схемой (см. states.py)
        """
        self.graph = StateGraph(GenerationState)
        self._build_graph()

    def _build_graph(self):
        
        """
        Просто добавление нод, времени почти не занимает
        """

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
        """
        __call__ - Дандер, который позволяет использовать объект класса как функцию
        Пример:
            generator = GenerationGraph()
            state = generation("Сделай мне диаграмму BPMN для процесса найма сотрудников")
            state = generator(state)
        """
        logger.info(f"Processing state: {state}")
        graph = self.compile()
        state = graph.invoke(state)
        logger.info(f"State after processing: {state}")
        return state


    def compile(self):
        """
        Для использования граф надо скомпилировать, это не занимает времени почти
        """
        logger.info("Compiling the graph")
        graph = self.graph.compile()
        logger.info("Graph compiled")
        return graph

    @staticmethod
    def entry_condition(state: GenerationState) -> str:
        """
        Условия в langgraph на вход принимают состояния, а выдают строки.
        entry_condition - входной роут, по состоянию определяющий направление
        Если диаграмма есть | if last in ["x6processor", "editor"] |, то роут на bpmn_condition
        Там проверяется, не нулевая ли диаграмма (это для запросов типа "Бот уничтожь диаграмму")
        Если диаграммы нет, то роут пойдет в диаграмму, на которой граф закончился - это для механики
        обратной связи, т.е. он всегда пойдет или в verifier, если это первый запрос, или в clarifier,
        если пришла обратная связь от пользователя (суть в том, что механика общей связи становится общей и
        можно придумывать еще ноды, использующие ее)
        """
        logger.info("Entry condition check")
        last = state["last"][1]
        if last in ["x6processor", "editor"]:
            logger.info("Entry condition met for bpmn condition")
            return "bpmn_condition"
        logger.info(f"Entry condition met for {last}")
        return last

    @staticmethod
    def verifier_node(state: GenerationState):
        """
        Нода верификации блочит запросы, не связанные с bpmn. Скорее всего, я потом verifier ноду просто
        началом сделаю или сделаю отдельную ноду, с отдельным агентом (промптом), который будет верифицировать,
        относится ли правки к диаграмме к уже сгенерирванной, но пока без этого, нода верификации срабатывает только
        в начале и там может при определенных условиях.
        Агент возвращает месседж с верификации
        state["agents_result"]["verifier"]["result"].get("reason")
        """
        state["last"] = ["generator", "verifier"]
        logger.info("Verifier agent is processing")
        verifier = Verifier(context=state["context"])
        state = verifier(state)
        logger.info("Verifier agent process ended")
        return state

    @staticmethod
    def verifier_condition(state: GenerationState) -> str:
        """
        Проход/выход из ноды верификации
        """
        logger.info("Verifier agent condition check")
        if state["agents_result"]["verifier"]["result"].get("is_bpmn_request"):
            return "clarifier"
        return END

    @staticmethod
    def clarifier_node(state: GenerationState):
        """
        Нода кларификации формирует обратную связь от LLM к юзеру
        Пример:
        User: Бот, сделай диаграмму
        Assistant: Что должно быть отражено в вашей диаграмме.

        Месседж с вопросом:
        state["agents_result"]["clarifier"]["result"].get("clarification")
        """
        state["last"] = ["generator", "clarifier"]
        logger.info("Clarifier agent is processing")
        if state["clarification_num_iterations"] <= 0:
            state["last"] = ["generator", "x6processor"]
            return state
        clarifier = Clarifier(context=state["context"])
        state = clarifier(state)
        state["clarification_num_iterations"] -= 1
        logger.info("Clarifier agent process ended")
        return state

    @staticmethod
    def clarifier_condition(state: GenerationState) -> str:
        """
        Выход/проход из кларифаера
        """
        logger.info("Clarifier agent condition check")
        if state["await_user_input"]:
            logger.info("User input exit condition met")
            return "user_input_exit"
        if state["clarification_num_iterations"] <= 0:
            logger.info("Clarification iterations ended")
            return "bpmn_condition"

    @staticmethod
    def x6processor_node(state: GenerationState):
        """
        Нода генерации графа, отличается от editor:
        во-первых, промптом
        во-вторых, ...)
        """
        state["last"] = ["generator", "x6processor"]
        logger.info("X6Processor agent is processing")
        x6processor = X6Processor(context=state["context"])
        state = x6processor(state)
        state["bpmn"] = state["agents_result"]["x6processor"]["result"]
        logger.info("X6Processor agent process ended")
        return state

    @staticmethod
    def editor_node(state: GenerationState):
        """
        Нода редакции графа. Обе ноды (x6processor, editor) работают
        только со структурой графа, т.е. существованием нод и их связями,
        расположение определяется сторонней функцией
        """
        state["last"] = ["generator", "editor"]
        logger.info("Editor agent is processing")
        editor = Editor(context=state["context"])
        state = editor(state)
        state["bpmn"] = state["agents_result"]["editor"]["result"]
        logger.info("Editor agent process ended")
        return state

    @staticmethod
    def bpmn_condition_node(state: GenerationState):
        """
        просто заглушка между условиями, функционала нет
        """
        return state

    @staticmethod
    def bpmn_condition(state: GenerationState) -> str:
        """
        Условие, роутящее граф при входе и не только,
        как и писал выше, это нужно для запросов,
        связанных с удалением графа полностью
        Внешне также нужно для обработки ошибок
        """
        logger.info("Generation agent check")
        if state["bpmn"] != {"nodes": [], "edges": []}:
            logger.info("BPMN is present")
            return "editor"
        logger.info("BPMN is not present")
        return "x6processor"

#
# query = ("Сделай мне диаграмму BPMN для процесса найма сотрудников. "
#          "Я хочу, чтобы она была простой и понятной. "
#          "Сделай так, чтобы она была на русском языке. "
#          "И добавь туда все необходимые элементы. "
#          "Список элементов: "
#          "1. Начало процесса\n"
#          "2. Сбор резюме\n"
#          "3. Проведение собеседования\n"
#          "4. Выбор кандидата\n"
#          "5. Проверка рекомендаций\n"
#          "6. Отправка предложения кандидату\n"
#          "7. Подписание контракта\n"
#          "8. Начало работы кандидата\n"
#          "9. Завершение процесса\n")
#
# state = generation(
#     user_input=query,
# )
#
# graph = GenerationGraph()
#
# state = graph(state)
#
# visualize_bpmn_graph(x6_layout(state["bpmn"]), "1")
#
# state["user_input"] = "Добавь в нее еще 5 элементов по теме диаграммы"
# state["await_user_input"] = False
# state = graph(state)
#
# print(state["bpmn"])
# visualize_bpmn_graph(x6_layout(state["bpmn"]), "2")
#
#
# state["user_input"] = "БОТ уничтожь диаграмму"
# state["await_user_input"] = False
#
# state = graph(state)
#
# print(state["bpmn"])
#
# state["user_input"] = "Бот верни диаграмму но на испанском языке"
#
# state["await_user_input"] = False