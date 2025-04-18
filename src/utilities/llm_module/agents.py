from src.utilities.llm_module.base_agent import BaseAgent
from src.utilities.llm_module.llm_constants import PROMPTS, MISTRAL_API_KEY, MODELS
from mistralai import Mistral
from mistralai.models import SystemMessage
import langid
import logging
from app.utils.logger import setup_logger
import json
from typing import List, Optional

logger = setup_logger("BaseAgent", logging.DEBUG)

CLIENT = Mistral(api_key=MISTRAL_API_KEY)


def mistral_call(messages: List[dict]) -> str:
    passed = False
    while not passed:
        try:
            response = CLIENT.chat.complete(
                model=MODELS["mistral"],
                messages=messages,
                safe_prompt=True
            )
            return response.choices[0].message.content
        except:
            passed = False


class Verifier(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["verification"], llm_call: callable = mistral_call,
                 context: Optional[List[dict]] = None):
        super().__init__(system_prompt, llm_call, context)


class Clarifier(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["clarification"], llm_call: callable = mistral_call,
                 context: Optional[List[dict]] = None):
        super().__init__(system_prompt, llm_call, context)

<<<<<<< HEAD:src/utilities/llm_module/agents.py

class Preprocessor(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["preprocessing"], llm_call: callable = mistral_call,
=======
class X6Processor(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["x6processing"], llm_call: callable = mistral_call,
>>>>>>> main:app/llm_module/agents.py
                 context: Optional[List[dict]] = None):
        super().__init__(system_prompt, llm_call, context)


class Editor(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["editing"], llm_call: callable = mistral_call,
                 context: Optional[List[dict]] = None):
        super().__init__(system_prompt, llm_call, context)

