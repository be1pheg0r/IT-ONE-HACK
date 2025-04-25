from pydantic import BaseModel, Field
from typing import Dict, Any, Union, List


class GenerationInput(BaseModel):
    """
    Входные параметры для запроса к агентам

    Attributes:
        user_input: Основной текст запроса для генерации диаграммы
    """

    user_input: str = Field(
        ...,
        example="Создать диаграмму для процесса найма сотрудников"
    )


class GenerationOutput(BaseModel):
    """
    Схема для выходных данных генерации BPMN диаграммы

    Attributes:
        output: Последнее из сообщений агентов (возможно, невалидное сообщение, если не удалось сгенерировать диаграмму)
    """

    output: Union[List[Dict], str] = Field(
        ...,
        example="Последнее из сообщений агентов (возможно, невалидное сообщение, если не удалось сгенерировать диаграмму)"
    )
