from src.utilities.debug.logger import setup_logger
from mistralai.models import SystemMessage, UserMessage, AssistantMessage
from typing import Callable, List, Optional, Dict
import uuid
from abc import ABC
from typing import List, Callable, Optional
import json
import logging
import langid
from src.utilities.llm_module.llm_constants import LANGUAGES

logger = logging.getLogger("BaseAgent")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

langid.set_languages(LANGUAGES)


logger = setup_logger("BaseAgent")


class BaseAgent(ABC):
    def __init__(self, system_prompt: str, llm_call: Callable,
                 context: Optional[List] = None):
        """
        :param system_prompt: Base system prompt for the agent
        :param llm_call: Function to call LLM: llm_call(messages: List[ChatMessage]) -> str
        :param context: Optional initial history as list of ChatMessage
        """
        self.system_prompt = system_prompt
        self.llm_call = llm_call
        # history of ChatMessage objects: SystemMessage, UserMessage, AssistantMessage
        self.history: List = context if context is not None else []
        logger.debug(
            f"{self._agent_role()} initialized. History length: {len(self.history)}")

    def __call__(self, state: Dict) -> Dict:
        user_input = state.get("user_input", "")
        logger.info(f"[{self._agent_role()}] Received input: {user_input}")

        # Append user message to history
        self.history.append(UserMessage(content=user_input))
        logger.debug(
            f"[{self._agent_role()}] Appended UserMessage. History length: {len(self.history)}")

        # Detect language code
        lang = langid.classify(user_input)[0]
        # Create system message including language hint
        sys_msg = SystemMessage(
            content=f"{self.system_prompt}{lang} language code")
        # Build messages list
        messages = [sys_msg] + self.history

        # Call LLM
        try:
            raw_response = self.llm_call(messages=messages)
            logger.debug(
                f"[{self._agent_role()}] LLM raw response: {raw_response}")
            response = self._process_response(raw_response)
        except Exception as e:
            logger.exception(
                f"[{self._agent_role()}] Error during LLM call or parsing: {e}")
            raise

        logger.info(f"[{self._agent_role()}] Parsed response: {response}")

        # Append assistant message
        self.history.append(AssistantMessage(content=raw_response))
        logger.debug(
            f"[{self._agent_role()}] Appended AssistantMessage. History length: {len(self.history)}")

        # Update state
        state["context"] = self.history
        logger.debug(f"[{self._agent_role()}] Updated state context.")
        state["agents_result"][self._agent_role()] = {
            "result": response,
            "await_user_input": bool(response.get("await_user_input"))
        }

        # Handle awaiting further user input
        if response.get("await_user_input"):
            state["await_user_input"] = True
            logger.info(f"[{self._agent_role()}] Awaiting user input set.")

        return state

    def _agent_role(self) -> str:
        return self.__class__.__name__.lower()

    def _process_response(self, raw: str) -> Dict:
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Response is not a JSON object")
            return data
        except json.JSONDecodeError as e:
            logger.error(
                f"[{self._agent_role()}] JSON decode error: {e}\nRaw: {raw}")
            raise
        except Exception as e:
            logger.error(
                f"[{self._agent_role()}] Response processing error: {e}")
            raise
