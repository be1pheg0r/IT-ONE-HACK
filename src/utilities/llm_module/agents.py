from src.utilities.llm_module.base_agent import BaseAgent
from src.utilities.llm_module.call_functions import mistral_call
from src.utilities.llm_module.llm_constants import PROMPTS, MISTRAL_API_KEY, MODELS
from typing import List, Optional
import logging

logger = logging.getLogger("Mistral")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class Verifier(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["verification"], llm_call: callable = mistral_call,
                 context: Optional[List[dict]] = None):
        super().__init__(system_prompt, llm_call, context)

class Clarifier(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["clarification"], llm_call: callable = mistral_call,
                 context: Optional[List[dict]] = None):
        super().__init__(system_prompt, llm_call, context)

class X6Processor(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["x6processing"], llm_call: callable = mistral_call,
                 context: Optional[List[dict]] = None):
        super().__init__(system_prompt, llm_call, context)


class Editor(BaseAgent):
    def __init__(self, system_prompt: str = PROMPTS["editing"], llm_call: callable = mistral_call,
                 context: Optional[List[dict]] = None):
        super().__init__(system_prompt, llm_call, context)

