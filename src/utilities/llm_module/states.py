from typing_extensions import TypedDict
from src.utilities.llm_module.llm_constants import CLARIFICATION_NUM_ITERATIONS, GENERATION_NUM_ITERATIONS
from typing import List, Dict


class AgentResult(TypedDict, total=False):
    result: dict
    await_user_input: bool


class BaseState(TypedDict):
    """
    АРГУМЕНТЫ СОСТОЯНИЯ
    -----------------------------
    user_input - запрос пользователя, для вызова графа надо обновить
    этот аргумент в состоянии и вызвать граф

    last - [{graph_name}, {agent_name}] - полезный аргумент, хранящий последнего выполняемого агента
    нужно для возвращения к графу после нового инпута от юзера

    context - все сообщения в типизации UserMessage, AssistantMessage и SystemMessage (возможно придется менять
    для локального инференса

    bpmn - диаграмма, просто аргумент для быстрого доступа

    agents_result - словарь, который хранит ПОСЛЕДНЕЕ срабатывание каждого агента, надо будет проапргейдить до
    хранения каждого результата агента, займусь

    await_user_input - флаг, указывающий на ожидание инпута
    """
    user_input: str
    last: List[str]
    context: List[dict]
    bpmn: List
    agents_result: Dict[str, List[AgentResult]]
    await_user_input: bool


class GenerationState(BaseState):
    """
    clarification_num_iterations - гиперпараметр (опционально), указывающий максимальную глубину петли уточнения
    пример:
    clarification_num_iterations = 2
    User: Бот сделать диаграмму
    Assistant: Что должно быть в вашей диаграмме?
    User: Процессы
    Assistant: Какие процессы?
    User: Разные
    Assistant: {Генерация графа}
    generation_num_iterations - гиперпараметр (опционально), указывающий на кол-во повторных генераций,
    при инвалидности предыдущих (сейчас не используется)
    """
    clarification_num_iterations: int
    generation_num_iterations: int


def generation(user_input: str, agents_result: Dict[str, Dict] = None, bpmn: List = None, last: List = None,
               context: List[dict] = None, await_user_input: bool = False,
               clarification_num_iterations: int = CLARIFICATION_NUM_ITERATIONS) -> GenerationState:
    """
    просто хэндлер под быстрое создания начального состояния
    """
    return GenerationState(
        user_input=user_input,
        agents_result=agents_result or {},
        clarification_num_iterations=clarification_num_iterations,
        generation_num_iterations=GENERATION_NUM_ITERATIONS,
        last=last or ["generator", "verifier"],
        bpmn=bpmn or {"nodes": [], "edges": []},
        context=context or [],
        await_user_input=await_user_input
    )
