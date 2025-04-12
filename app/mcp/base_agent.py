from abc import ABC, abstractmethod
from typing import List
import json


class BaseAgent (ABC):
    @abstractmethod
    def __init__(self, system_prompt: str, llm_call: callable, context: dict):
        """

        :param system_prompt: Системный промпт для агента
        :param llm_call: Функция вызова ЛЛМ
        :param context:
        КОНТЕКСТ:
        {
            "messages": [],
            "agent_results": []
        }
        """
        self.system_prompt: str = system_prompt
        self.llm_call: callable = llm_call
        if context is None:
            context = {
                "messages": [],
                "agent_results": []
            }
        self.messages: List[dict] = context["messages"]
        self.agent_results: List[dict] = context["agent_results"]

    def _process_response(self, response: str) -> dict:
        try:
            result = json.loads(response)
            if not isinstance(result, dict):
                raise ValueError("Response is not a valid JSON object")
            return result
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}")

    def _agent_role(self) -> str:
        return self.__class__.__name__.lower()

    def _add_user_message(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})

    def _add_agent_result(self, result: dict):
        self.agent_results.append({self._agent_role(): result})


    def _get_user_inputs(self) -> List[str]:
        return [msg["content"] for msg in self.messages if msg["role"] == "user"]

    @abstractmethod
    def _build_final_prompt(self, user_input: str) -> str:
        pass




