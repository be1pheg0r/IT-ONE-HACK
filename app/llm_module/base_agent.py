from abc import ABC
from typing import List, Callable, Optional
import json
import logging
import langid
from app.llm_module.llm_constants import LANGUAGES

logger = logging.getLogger("BaseAgent")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

langid.set_languages(LANGUAGES)

class BaseAgent(ABC):
    def __init__(self, system_prompt: str, llm_call: Callable, context: Optional[List[dict]] = None):
        self.system_prompt: str = system_prompt
        self.llm_call: Callable = llm_call
        self.history: List[dict] = context if context is not None else []
        logger.debug(f"{self._agent_role()} initialized with system prompt.")

    def __call__(self, state: dict) -> dict:
        user_input = state["user_input"]
        logger.info(f"[{self._agent_role()}] Received input: {user_input}")

        self._add_to_history({"role": "user", "content": user_input})
        history = self._build_history()
        prompt = self._build_final_prompt(user_input, history)

        logger.debug(f"[{self._agent_role()}] Built prompt: {prompt}")

        try:
            raw_response = self.llm_call(messages=history, system_prompt=prompt)
            logger.debug(f"[{self._agent_role()}] LLM raw response: {raw_response}")
            response = self._process_response(raw_response)
        except Exception as e:
            logger.exception(f"[{self._agent_role()}] Error during LLM call or response parsing: {e}")
            raise

        logger.info(f"[{self._agent_role()}] Parsed response: {response}")

        self._add_to_history({"role": "assistant", "content": json.dumps({self._agent_role(): response}, ensure_ascii=False)})

        state[f"{self._agent_role()}_result"] = response
        state["context"] = self.history

        if response.get("await_user_input"):
            state["await_user_input"] = True
            logger.info(f"[{self._agent_role()}] Awaiting user input set.")

        return state

    def _build_final_prompt(self, user_input: str, history: List[dict]) -> str:
        lang = langid.classify(user_input)[0]
        final_prompt = (
            f"{self.system_prompt}"
            f"{lang} language code\n\n"
            f"###########################################\n\n"
            f"History of the conversation:\n"
            f"{json.dumps(history, ensure_ascii=False)}\n\n"
        )
        logger.info(f"[{self._agent_role()}] Final prompt built: {final_prompt}")
        return final_prompt

    def _build_history(self) -> List[dict]:
        return self.history

    def _agent_role(self) -> str:
        return self.__class__.__name__.lower()

    def _add_to_history(self, message: dict):
        self.history.append(message)
        logger.debug(f"[{self._agent_role()}] Added to history: {message}")

    def _get_user_inputs(self) -> List[str]:
        return [entry["content"] for entry in self.history if entry["role"] == "user"]

    def _get_agent_results(self) -> List[dict]:
        results = []
        for entry in self.history:
            if entry["role"] == "assistant":
                try:
                    result = json.loads(entry["content"])
                    results.append(result)
                except json.JSONDecodeError:
                    logger.warning(f"[{self._agent_role()}] Could not decode assistant message: {entry['content']}")
        return results

    def _process_response(self, response: str) -> dict:
        try:
            result = json.loads(response)
            if not isinstance(result, dict):
                raise ValueError("Response is not a valid JSON object")
            return result
        except Exception as e:
            logger.error(f"[{self._agent_role()}] Failed to parse response: {response}")
            raise ValueError(f"Failed to parse agent response: {e}")