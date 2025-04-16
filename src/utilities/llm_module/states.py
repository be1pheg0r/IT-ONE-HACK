from typing_extensions import TypedDict
from src.utilities.llm_module.llm_constants import CLARIFICATION_NUM_ITERATIONS
from typing import List


class MainState(TypedDict):
    user_input: str
    current: List
    agents_result: dict
    context: List[dict]
    clarification_num_iterations: int


def main(user_input: str, agents_result: dict = None, current: List = None, context: List[dict] = None, clarification_num_iterations: int = CLARIFICATION_NUM_ITERATIONS) -> MainState:
    if agents_result is None:
        agents_result = {}

    if current is None:
        current = ["main", "basic_entry"]

    if context is None:
        context = []

    return {
        "user_input": user_input,
        "agents_result": agents_result,
        "current": current,
        "context": context,
        "clarification_num_iterations": clarification_num_iterations
    }
