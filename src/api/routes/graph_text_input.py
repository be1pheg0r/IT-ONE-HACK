from fastapi import APIRouter
from src.utilities.llm_module.src.markup_to_x6 import x6_layout
from src.utilities.llm_module.graphs import GenerationGraph
from src.utilities.llm_module.states import generation
from src.models.schemas.graphs_output import GenerationInput, GenerationOutput
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer


router = APIRouter(prefix="/user_input", tags=["user_input"])

model_path = "solidrust/Nous-Hermes-2-Mistral-7B-DPO-AWQ"

model = AutoAWQForCausalLM.from_quantized(model_path, fuse_layers=True)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)


# только для MVP, потом заменить на бд
STATE = None
MODE = "local"
LOCAL_MODEL_CFG = {
    "model": model,
    "tokenizer": tokenizer,
}


def generate_output(input_data: str, mode: str, local_model_cfg=None) -> GenerationOutput:
    """
    :param input_data: Входные параметры для генерации диаграммы
    :param process_query: Базовый промпт работы модели
    :return: BPMN диаграмма и дополнительная информация о процессе
    """
    global STATE
    if not STATE:
        STATE = generation(input_data)
    else:
        STATE["user_input"].append(input_data)

    graph = GenerationGraph(mode=mode, local_model_cfg=local_model_cfg)
    STATE = graph(STATE)
    last = STATE["last"][-1][1]
    output = STATE["agents_result"][last][-1]["content"]
    if last in ["x6processor", "editor"]:
        output = x6_layout(output)
    return GenerationOutput(output=output)


@router.post("/text", summary="Получить граф", response_model=GenerationOutput)
async def get_json_graph(user: GenerationInput) -> GenerationOutput:
    """
    :param input_data: Входные параметры для генерации диаграммы
    :return: BPMN диаграмма и дополнительная информация о процессе
    """

    return generate_output(user.user_input, 'api')
