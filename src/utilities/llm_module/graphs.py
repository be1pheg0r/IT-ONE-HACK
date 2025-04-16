import logging
import langgraph
from langgraph.graph import StateGraph, START
from src.utilities.llm_module.states import MainState
from src.utilities.llm_module.agents import Verifier, Clarifier, Preprocessor
from src.utilities.llm_module.src.markup_to_x6 import x6_layout

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MainGraph:
    def __init__(self):
        logger.info("Initializing MainGraph.")
        self.graph = StateGraph(MainState)
        self._entries = ["basic_entry", "after_clarifying_entry"]
        self._agents = ["verifier", "clarifier", "preprocessor"]
        self._exits = ["verifier_exit", "clarifier_exit", "preprocessor_exit"]
        self._build_graph()

    def _build_graph(self):
        logger.info("Building graph structure.")
        for entry in self._entries:
            self.graph.add_node(entry, getattr(self, f"{entry}_node"))
        for agent in self._agents:
            self.graph.add_node(agent, getattr(self, f"{agent}_node"))
        for exit in self._exits:
            self.graph.add_node(exit, getattr(self, f"{exit}_node"))

        self.graph.add_edge("basic_entry", "verifier")

        self.graph.add_conditional_edges(
            START, self.entry_condition,
            {i: i for i in self._entries}
        )

        self.graph.add_conditional_edges(
            "after_clarifying_entry", self.after_clarifying_condition,
            {i: i for i in ["preprocessor", "clarifier"]}
        )

        self.graph.add_conditional_edges(
            "verifier", self.verifier_condition,
            {i: i for i in ["verifier_exit", "clarifier"]}
        )

        self.graph.add_conditional_edges(
            "clarifier", self.clarifier_condition,
            {i: i for i in ["preprocessor", "clarifier_exit"]}
        )

        self.graph.add_edge("preprocessor", "preprocessor_exit")
        logger.info("Graph structure built successfully.")

    def __call__(self, state: MainState) -> dict:
        logger.info("Starting MainGraph invocation.")
        graph = self.compile()
        state = graph.invoke(state)
        logger.info("MainGraph invocation completed.")
        return state

    def reset_graph(self):
        logger.info("Resetting graph.")
        self.graph = StateGraph(MainState)
        self._build_graph()
        logger.info("Graph reset successfully.")

    def compile(self) -> langgraph.graph.state.CompiledGraph:
        logger.info("Compiling graph.")
        graph = self.graph.compile()
        logger.info("Graph compiled successfully.")
        return graph

    @staticmethod
    def basic_entry_node(state: MainState) -> dict:
        logger.info("Entry is basic.")
        state["current"] = ["main", "basic_entry"]
        return state

    @staticmethod
    def after_clarifying_entry_node(state: MainState) -> dict:
        logger.info("Entry is after clarifying.")
        state["current"] = ["main", "after_clarifying"]
        return state

    @staticmethod
    def after_clarifying_condition(state: MainState) -> str:
        logger.info("Evaluating after clarifying condition.")
        if state["clarification_num_iterations"] > 0:
            logger.info("Clarification needed. Returning to clarifier.")
            return "clarifier"
        logger.info("No clarification needed. Proceeding to preprocessor.")
        return "preprocessor"

    def entry_condition(self, state: MainState) -> str:
        logger.info("Check entry condition.")
        entry = state["current"][1]
        if entry in self._entries:
            return entry
        else:
            return "basic_entry"

    @staticmethod
    def verifier_node(state: MainState) -> dict:
        state["current"] = ["main", "verifier"]
        logger.info("Executing verifier node.")
        verifier = Verifier(context=state["context"])
        verifier_result = verifier(state)["verifier_result"]
        state["agents_result"]["verifier_result"] = verifier_result
        state["context"] = verifier.history
        logger.info(f"Verifier node executed successfully."
                    f"Returned state: {state}")
        return state

    @staticmethod
    def verifier_condition(state: MainState) -> str:
        logger.info("Evaluating verifier condition.")
        if state["agents_result"]["verifier_result"]["is_bpmn_request"] in [True, "true"]:
            logger.info("Verifier condition met: Redirecting to clarifier.")
            return "clarifier"
        logger.info("Verifier condition not met: verifier exit.")
        return "verifier_exit"

    @staticmethod
    def clarifier_node(state: MainState) -> dict:
        state["current"] = ["main", "clarifier"]
        logger.info("Executing clarifier node.")
        clarifier = Clarifier(context=state["context"])
        clarifier_result = clarifier(state)["clarifier_result"]
        state["agents_result"]["clarifier_result"] = clarifier_result
        state["context"] = clarifier.history
        state["clarification_num_iterations"] -= 1
        logger.info(f"Clarifier node executed successfully."
                    f"Returned state: {state}")
        return state

    @staticmethod
    def clarifier_condition(state: MainState) -> str:
        logger.info("Evaluating clarifier condition.")
        if state["agents_result"]["clarifier_result"]["clarification_needed"] in [True, "true"]:
            if state["clarification_num_iterations"] >= 0:
                logger.info("Clarification needed. clarifier exit.")
                return "clarifier_exit"
        logger.info("No clarification needed; redirecting to preprocessor.")
        return "preprocessor"

    @staticmethod
    def user_reply_node(state: MainState) -> dict:
        pass

    @staticmethod
    def preprocessor_node(state: MainState) -> dict:
        logger.info("Executing preprocessor node.")
        preprocessor = Preprocessor(context=state["context"])
        preprocessor_result = preprocessor(state)["preprocessor_result"]
        state["agents_result"]["preprocessor_result"] = x6_layout(
            preprocessor_result)
        state["context"] = preprocessor.history
        state["current"] = ["main", "preprocessor"]
        logger.info(f"Preprocessor node executed successfully."
                    f"Returned state: {state}")
        return state

    @staticmethod
    def preprocessor_exit_node(state: MainState) -> dict:
        state["current"] = ["main", "preprocessor_exit"]
        logger.info("There was preprocessor exit.")
        return state

    @staticmethod
    def verifier_exit_node(state: MainState) -> dict:
        state["current"] = ["main", "verifier_exit"]
        logger.info("There was verifier exit")
        return state

    @staticmethod
    def clarifier_exit_node(state: MainState) -> dict:
        state["current"] = ["main", "clarifier_exit"]
        logger.info("There was clarifier exit")
        return state
