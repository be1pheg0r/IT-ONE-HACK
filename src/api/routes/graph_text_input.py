from fastapi import APIRouter
from src.utilities.llm_module.src.markup_to_x6 import x6_layout
from src.utilities.llm_module.graphs import GenerationGraph
from src.utilities.llm_module.states import generation
from src.models.schemas.bpmn import BPMNGenerationInput, BPMNGenerationOutput
from src.utilities.llm_module.llm_constants import DEFAULT_HIRING_PROCESS_QUERY


router = APIRouter(prefix="/user_input", tags=["user_input"])


def generate_bpmn_diagram(input_data: BPMNGenerationInput, process_query: str = DEFAULT_HIRING_PROCESS_QUERY) -> BPMNGenerationOutput:
    """
    :param input_data: Входные параметры для генерации диаграммы
    :param process_query: Базовый промпт работы модели
    :return: BPMN диаграмма и дополнительная информация о процессе
    """

    state = generation(user_input=process_query)
    graph = GenerationGraph()

    state = graph(state)

    state["user_input"] = input_data

    # Нужна будет база данных для хранения состояний контекста
    state["await_user_input"] = False

    state = graph(state)

    return {"data": x6_layout(BPMNGenerationOutput(
        bpmn=state["bpmn"]
    ))}


@router.post("/text", summary="Получить граф", response_model=BPMNGenerationOutput)
async def get_json_graph(user: BPMNGenerationInput) -> BPMNGenerationOutput:
    """
    :param input_data: Входные параметры для генерации диаграммы
    :return: BPMN диаграмма и дополнительная информация о процессе
    """

    return generate_bpmn_diagram(user.user_input)
