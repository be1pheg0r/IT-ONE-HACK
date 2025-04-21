from abc import ABC
from typing import List, Callable, Optional
import json
import logging
import langid
from src.utilities.llm_module.llm_constants import LANGUAGES
from typing import Dict
from mistralai.models import SystemMessage, UserMessage, AssistantMessage

logger = logging.getLogger("Base_agent")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

langid.set_languages(LANGUAGES)


class BaseAgent(ABC):
    def __init__(self, system_prompt: str, llm_call: Callable,
                 context: Optional[List] = None):
        self.system_prompt = system_prompt
        self.llm_call = llm_call
        self.history: List = context if context is not None else []
        logger.debug(
            f"{self._agent_role()} initialized. History length: {len(self.history)}")

    def __call__(self, state: Dict) -> Dict:
        user_input = state.get("user_input", "")
        logger.info(f"[{self._agent_role()}] Received input: {user_input}")

        self.history.append(UserMessage(content=user_input))
        logger.debug(
            f"[{self._agent_role()}] Appended UserMessage. History length: {len(self.history)}")

        lang = langid.classify(user_input)[0]
        sys_msg = SystemMessage(
            content=f"{self.system_prompt}{lang} language code")
        messages = [sys_msg] + self.history

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

        self.history.append(AssistantMessage(content=raw_response))
        logger.debug(
            f"[{self._agent_role()}] Appended AssistantMessage. History length: {len(self.history)}")

        state["context"] = self.history
        logger.debug(f"[{self._agent_role()}] Updated state context.")
        if self._agent_role() not in state["agents_result"].keys():
            state["agents_result"][self._agent_role()] = []
        state["agents_result"][self._agent_role()].append({
            "result": response,
            "await_user_input": bool(response.get("await_user_input"))
        })

        if response.get("await_user_input"):
            state["await_user_input"] = True
            logger.info(f"[{self._agent_role()}] Awaiting user input set.")

        return state

    def _agent_role(self) -> str:
        return self.__class__.__name__.lower()

    def _process_response(self, raw: str) -> Dict:
        try:
            data = json.loads(raw.strip().strip('```').strip('json'))
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
