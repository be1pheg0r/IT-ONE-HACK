from typing_extensions import TypedDict
<<<<<<< HEAD:src/utilities/llm_module/states.py
from src.utilities.llm_module.llm_constants import CLARIFICATION_NUM_ITERATIONS
from typing import List
=======
from app.llm_module.llm_constants import CLARIFICATION_NUM_ITERATIONS, GENERATION_NUM_ITERATIONS
from typing import List, Dict
>>>>>>> main:app/llm_module/states.py


class AgentResult(TypedDict, total=False):
    result: dict
    await_user_input: bool


class BaseState(TypedDict):
    user_input: str
    current: List[str]
    context: List[dict]
    bpmn: List
    agents_result: Dict[str, AgentResult]
    await_user_input: bool


class GenerationState(BaseState):
    clarification_num_iterations: int
    generation_num_iterations: int


class MainState(BaseState):
    states: dict[str, BaseState]

<<<<<<< HEAD:src/utilities/llm_module/states.py
    return {
        "user_input": user_input,
        "agents_result": agents_result,
        "current": current,
        "context": context,
        "clarification_num_iterations": clarification_num_iterations
    }
=======

class EditingState(BaseState):
    pass


def generation(user_input: str, agents_result: Dict[str, Dict] = None, bpmn: List = None, current: List = None,
               context: List[dict] = None, await_user_input: bool = False,
               clarification_num_iterations: int = CLARIFICATION_NUM_ITERATIONS) -> GenerationState:
    return GenerationState(
        user_input=user_input,
        agents_result=agents_result or {},
        clarification_num_iterations=clarification_num_iterations,
        generation_num_iterations=GENERATION_NUM_ITERATIONS,
        current=current or ["generator", "verifier"],
        bpmn=bpmn or [],
        context=context or [],
        await_user_input=await_user_input
    )


def main(user_input: str, states: Dict[str, Dict] = None, agents_result: Dict[str, Dict] = None, current: List = None,
         bpmn: List = None, await_user_input: bool = False,
         context: List[dict] = None) -> MainState:
    return MainState(
        user_input=user_input,
        states=states or {},
        agents_result=agents_result or {},
        current=current or ["main", "basic_entry"],
        bpmn=bpmn or [],
        context=context or [],
        await_user_input=await_user_input
    )
>>>>>>> main:app/llm_module/states.py
