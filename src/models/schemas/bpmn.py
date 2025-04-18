from pydantic import BaseModel, Field
from typing import Dict, Any


class BPMNGenerationInput(BaseModel):
    """
    Входные параметры для генерации BPMN диаграммы

    Attributes:
        user_input: Основной текст запроса для генерации диаграммы
    """

    user_input: str = Field(
        ...,
        example="Создай BPMN диаграмму для процесса обработки заявок",
        description="Текстовое описание желаемого процесса"
    )


class BPMNGenerationOutput(BaseModel):
    """
    Результат генерации BPMN диаграммы

    Attributes:
        bpmn: Сгенерированная диаграмма в формате JSON
    """

    bpmn: Dict[str, Any] = Field(
        ...,
        example={
            "nodes": [{"id": "start", "type": "startEvent"}],
            "edges": []
        },
        description="BPMN диаграмма в формате JSON"
    )
