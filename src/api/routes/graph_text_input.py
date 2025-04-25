from fastapi import APIRouter
from src.utilities.llm_module.src.markup_to_x6 import x6_layout
from src.utilities.llm_module.graphs import GenerationGraph
from src.utilities.llm_module.states import GenerationState, generation
from src.models.schemas.bpmn import BPMNGenerationInput, BPMNGenerationOutput
from src.utilities.llm_module.llm_constants import DEFAULT_HIRING_PROCESS_QUERY


router = APIRouter(prefix="/user_input", tags=["user_input"])


def generate_bpmn_diagram(input_data: BPMNGenerationInput, mode: str, local_model_cfg=None, state: GenerationState = None) -> BPMNGenerationOutput:
    """
    :param input_data: Входные параметры для генерации диаграммы
    :param process_query: Базовый промпт работы модели
    :return: BPMN диаграмма и дополнительная информация о процессе
    """

    generator = GenerationGraph(mode='api', local_model_cfg='None')
    if state:
        state["user_input"].append(input_data)
    else:
        state = generation(user_input=input_data)
    state = generator(state)

    return {"bpmn": x6_layout(
        state["bpmn"][-1]
    )}


@router.post("/text", summary="Получить граф", response_model=BPMNGenerationOutput)
async def get_json_graph(user: BPMNGenerationInput) -> BPMNGenerationOutput:
    """
    :param input_data: Входные параметры для генерации диаграммы
    :return: BPMN диаграмма и дополнительная информация о процессе
    """

    return generate_bpmn_diagram(user.user_input, 'api')
