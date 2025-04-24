from mistralai import Mistral
from mistralai.models import SystemMessage, UserMessage, AssistantMessage
from src.utilities.llm_module.llm_constants import MISTRAL_API_KEY, MODELS
from typing import List, Dict, Union
import torch
import logging

# Настройка логирования
logger = logging.getLogger("Mistral")
logger.setLevel(logging.DEBUG)


def _preprocess_context(context: List[Union[UserMessage, SystemMessage, AssistantMessage]]) -> List[Dict[str, str]]:
    """
    Функция для обработки контекста и преобразования его в формат, подходящий для передачи в модель.
    """
    processed_context = []
    for message in context:
        processed_context.append({"role": message.role, "content": message.content})
    return processed_context


def mistral_call(messages: List[Union[UserMessage, SystemMessage, AssistantMessage]]) -> str:
    passed = False
    client = Mistral(api_key=MISTRAL_API_KEY)
    while not passed:
        try:
            response = client.chat.complete(
                model=MODELS["mistral_api"],
                messages=messages,
                safe_prompt=True
            )
            return response.choices[0].message.content
        except Exception as e:
            # logger.exception(f"Error during Mistral API call: {e}")
            continue


def mistral_local_call(messages: List[Union[UserMessage, SystemMessage, AssistantMessage]], local_model_cfg) -> str:
    """
    Функция для вызова модели Mistral local с использованием библиотеки transformers.
    """
    model = local_model_cfg["model"]
    tokenizer = local_model_cfg["tokenizer"]
    prompt = tokenizer.apply_chat_template(_preprocess_context(messages), tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt")
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        tokens = model.generate(
            **inputs,
            max_new_tokens=1024,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
    output_text = tokenizer.decode(tokens[0], skip_special_tokens=True)
    return output_text.split("assistant\n")[-1]
