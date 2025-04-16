from src.utilities.llm_module.base_agent import BaseAgent
from src.utilities.llm_module.llm_constants import PROMPTS, MISTRAL_API_KEY, MODELS
from mistralai import Mistral
from mistralai.models import SystemMessage
from typing import List, Optional

CLIENT = Mistral(api_key=MISTRAL_API_KEY)


def mistral_call(messages: List[dict], system_prompt: str) -> str:
    passed = False
    while not passed:
        try:
            response = CLIENT.chat.complete(
                model=MODELS["mistral"],
                messages=[SystemMessage(content=system_prompt)] + messages,
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


class Preprocessor(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["preprocessing"], llm_call: callable = mistral_call,
                 context: Optional[List[dict]] = None):
        super().__init__(system_prompt, llm_call, context)
