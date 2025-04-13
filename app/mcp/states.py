from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from app.mcp.llm_constants import CLARIFICATION_NUM_ITERATIONS

class State(TypedDict):
    user_input: str
    verifier_result: dict
    clarifier_result: dict
    preprocessor_result: list
    context: dict
    clarification_num_iterations: int

def default(user_input: str) -> State:
    return {
        "user_input": user_input,
        "verifier_result": {},
        "clarifier_result": {},
        "preprocessor_result": [],
        "context": {
            "messages": [],
            "agent_results": []
        },
        "clarification_num_iterations": CLARIFICATION_NUM_ITERATIONS
    }
