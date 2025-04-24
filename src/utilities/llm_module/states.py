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
    * user_input - List[str] - список с запросами пользователя, для вызова графа надо добавить в лист
    новый запрос и вызвать граф

    * last - List[List[str]] - полезный аргумент, хранящий срабатывание агентов, в виде списка с именем графа и
    именем агента, который сработал, например: ["generator", "verifier"], ["generator", "clarifier"] и т.д.

    * context - List[dict] - все сообщения в типизации UserMessage, AssistantMessage и SystemMessage (возможно придется менять
    для локального инференса

    * bpmn - List[List[dict]] - список диаграмм, полученных от генератора или редактора. Если одной из диаграмм не
    присваиваются координаты (ошибка генерации на стороне LLM), то можно вернуть предыдущую диаграмму из списка

    * agents_result - Dict[str, List[AgentResult]] - словарь, который хранит все результаты агентов

    * await_user_input - флаг, указывающий на ожидание инпута (служебный)
    """
    user_input: List[str]
    last: List[List[str]]
    context: List[dict]
    bpmn: List[List[dict]]
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


def generation(user_input: str,
               last: List[List[str]] = None,
               context: List[dict] = None,
               bpmn: List[List[dict]] = None,
               agents_result: Dict[str, List[AgentResult]] = None,
               await_user_input: bool = False) -> GenerationState:
    """
    Функция генерации состояния для графа генерации (только для инициации)
    """
    return {
        "user_input": [user_input],
        "last": last if last is not None else [],
        "context": context if context is not None else [],
        "bpmn": bpmn if bpmn is not None else [],
        "agents_result": agents_result if agents_result is not None else {},
        "await_user_input": await_user_input,
        "clarification_num_iterations": CLARIFICATION_NUM_ITERATIONS,
        "generation_num_iterations": GENERATION_NUM_ITERATIONS
    }