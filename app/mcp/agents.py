from app.mcp.base_agent import BaseAgent
from app.mcp.llm_constants import PROMPTS, CLARIFICATION_NUM_ITERATIONS, MISTRAL_API_KEY, MODELS
import json
from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage

CLIENT = Mistral(api_key=MISTRAL_API_KEY)


def mistral_call(user_prompt: str, system_prompt: str, ignore_mistral_errors: bool = True) -> str:
    passed = False
    while not passed:
        try:
            response = CLIENT.chat.complete(
                model=MODELS["mistral"],
                messages=[
                    SystemMessage(content=system_prompt),
                    UserMessage(content=user_prompt)
                ],
                safe_prompt=True
            )
            passed = True
            return response.choices[0].message.content
        except Exception as e:
            if not ignore_mistral_errors:
                print(f"Error: {e}")
                print("Retrying...")


class Verifier(BaseAgent):

    def __init__(self, system_prompt: str = PROMPTS["verification"], llm_call: callable = mistral_call,
                 context: dict = None):
        super().__init__(system_prompt, llm_call, context)
        self._system_prompt = system_prompt
        self._llm_call = llm_call
        self._messages = context["messages"] if context else []
        self._agent_results = context["agent_results"] if context else []

    def __call__(self, state: dict) -> dict:
        user_input = state["user_input"]
        final_prompt = self._build_final_prompt(user_input)
        response = self.llm_call(user_input, final_prompt)
        response = self._process_response(response)
        self._add_agent_result(response)
        return response

    def _build_final_prompt(self, user_input: str) -> str:
        self._add_user_message(user_input)
        user_inputs = self._get_user_inputs()
        # request - response history
        history = []
        for i in range(len(user_inputs)):
            history.append({"role": "user", "content": user_inputs[i]})
            if i < len(self._agent_results):
                history.append({"role": "assistant", "content": self._agent_results[i]})

        final_prompt = (f"{self._system_prompt}\n\n"
                        f"History of the conversation:\n"
                        f"{json.dumps(history, ensure_ascii=False)}\n\n")
        return final_prompt


class Clarifier(BaseAgent):

    def __init__(self, system_prompt: str = PROMPTS["clarification"], llm_call: callable = mistral_call,
                 context: dict = None):
        super().__init__(system_prompt, llm_call, context)
        self._system_prompt = system_prompt
        self._llm_call = llm_call
        self._messages = context["messages"] if context else []
        self._agent_results = context["agent_results"] if context else []

    def __call__(self, state: dict) -> dict:
        user_input = state["user_input"]
        final_prompt = self._build_final_prompt(user_input)
        response = self.llm_call(user_input, final_prompt)
        response = self._process_response(response)
        self._add_agent_result(response)
        return response

    def _build_final_prompt(self, user_input: str) -> str:
        self._add_user_message(user_input)
        user_inputs = self._get_user_inputs()
        history = []
        for i in range(len(user_inputs)):
            history.append({"role": "user", "content": user_inputs[i]})
            if i < len(self._agent_results):
                history.append({"role": "assistant", "content": self._agent_results[i]})

        final_prompt = (f"{self._system_prompt}\n\n"
                        f"History of the conversation:\n"
                        f"{json.dumps(history, ensure_ascii=False)}\n\n")
        return final_prompt


class Preprocessor(BaseAgent):

    def __init__(self, system_prompt: str = PROMPTS["preprocessing"], llm_call: callable = mistral_call,
                 context: dict = None):
        super().__init__(system_prompt, llm_call, context)
        self._system_prompt = system_prompt
        self._llm_call = llm_call
        self._messages = context["messages"] if context else []
        self._agent_results = context["agent_results"] if context else []

    def __call__(self, state: dict) -> dict:
        user_input = state["user_input"]
        final_prompt = self._build_final_prompt(user_input)
        response = self.llm_call(user_input, final_prompt)
        response = self._process_response(response)
        self._add_agent_result(response)
        return response

    def _build_final_prompt(self, user_input: str) -> str:
        self._add_user_message(user_input)
        user_inputs = self._get_user_inputs()
        history = []
        for i in range(len(user_inputs)):
            history.append({"role": "user", "content": user_inputs[i]})
            if i < len(self._agent_results):
                history.append({"role": "assistant", "content": self._agent_results[i]})

        final_prompt = (f"{self._system_prompt}\n\n"
                        f"History of the conversation:\n"
                        f"{json.dumps(history, ensure_ascii=False)}\n\n")
        return final_prompt

    def preprocess(self, user_input: str) -> dict:
        final_prompt = self._build_final_prompt(user_input)
        response = self.llm_call(user_input, final_prompt)
        response = self._process_response(response)
        return response

