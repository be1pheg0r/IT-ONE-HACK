import logging
import langgraph
from langgraph.graph import StateGraph, END
from app.mcp.states import State, default
from app.mcp.agents import Verifier, Clarifier, Preprocessor
from app.mcp.services.markup_to_x6 import x6_layout

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class BPMNFlow:

    def __init__(self, verbose: bool = True):
        logger.info("Initializing BPMNFlow.")
        self.graph = StateGraph(State)
        self._compiled = False
        self._build_graph()
        if not verbose:
            logger.setLevel(logging.WARNING)

    def _build_graph(self):
        logger.info("Building graph structure.")
        self._compiled = False
        self.graph.add_node("verifier", self.verifier_node)
        self.graph.set_entry_point("verifier")
        self.graph.add_node("clarifier", self.clarifier_node)
        self.graph.add_node("preprocessor", self.preprocessor_node)

        self.graph.add_conditional_edges(
            "verifier", self.verifier_condition,
            {"clarifier": "clarifier", END: END}
        )

        self.graph.add_conditional_edges(
            "clarifier", self.clarifier_condition,
            {"clarifier": "clarifier", "preprocessor": "preprocessor", END: END}
        )

        self.graph.add_edge("preprocessor", END)
        logger.info("Graph structure built successfully.")

    def __call__(self, state: State) -> dict:
        logger.info("Starting BPMNFlow invocation.")
        graph = self.compile()
        state = graph.invoke(state)
        logger.info("BPMNFlow invocation completed.")
        return state

    def reset_graph(self):
        logger.info("Resetting graph.")
        self.graph = StateGraph(State)
        self._build_graph()
        logger.info("Graph reset successfully.")

    def compile(self) -> langgraph.graph.state.CompiledGraph:
        logger.info("Compiling graph.")
        graph = self.graph.compile()
        logger.info("Graph compiled successfully.")
        return graph

    @staticmethod
    def verifier_node(state: State) -> dict:
        logger.info("Executing verifier node.")
        verifier = Verifier(context=state["context"])
        verifier_result = verifier(state)
        state["verifier_result"] = verifier_result
        state["context"] = verifier.get_context()
        logger.info("Verifier node executed successfully.")
        return state

    @staticmethod
    def verifier_condition(state: State) -> str:
        logger.info("Evaluating verifier condition.")
        if state["verifier_result"]["is_bpmn_request"] == "true":
            logger.info("Verifier condition met: Redirecting to clarifier.")
            return "clarifier"
        logger.info("Verifier condition not met: Ending.")
        return END

    @staticmethod
    def clarifier_node(state: State) -> dict:
        logger.info("Executing clarifier node.")
        clarifier = Clarifier(context=state["context"])
        clarifier_result = clarifier(state)
        state["clarifier_result"] = clarifier_result
        state["context"] = clarifier.get_context()
        logger.info("Clarifier node executed successfully.")
        return state

    @staticmethod
    def clarifier_condition(state: State) -> str:
        logger.info("Evaluating clarifier condition.")
        if state["clarifier_result"]["clarification_needed"] == "true":
            if state["clarification_num_iterations"] > 0:
                state["clarification_num_iterations"] -= 1
                logger.info("Clarification needed; iterating clarifier node again.")
                return "clarifier"
            else:
                logger.info("Clarification limit reached: Ending.")
                return END
        logger.info("No clarification needed; redirecting to preprocessor.")
        return "preprocessor"

    @staticmethod
    def preprocessor_node(state: State) -> dict:
        logger.info("Executing preprocessor node.")
        preprocessor = Preprocessor(context=state["context"])
        preprocessor_result = preprocessor(state)
        state["preprocessor_result"] = x6_layout(preprocessor_result)
        logger.info("Preprocessor node executed successfully.")
        return state