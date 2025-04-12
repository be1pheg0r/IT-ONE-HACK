from base_agent import BaseAgent
from llm_constants import SYSTEM_PROMPT_CLARIFICATION_NODE, SYSTEM_PROMPT_GENERATION_NODE, \
    SYSTEM_PROMPT_VERIFICATION_NODE, CLARIFICATION_NUM_ITERATIONS
import json
import os
from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
CLIENT = Mistral(api_key=MISTRAL_API_KEY)
MODEL = "ministral-8b-latest"


def llm_call(user_prompt: str, system_prompt: str) -> str:
    passed = False
    while not passed:
        try:
            response = CLIENT.chat.complete(
                model=MODEL,
                messages=[
                    SystemMessage(content=system_prompt),
                    UserMessage(content=user_prompt)
                ],
                safe_prompt=True
            )
            passed = True
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            print("Retrying...")


class Clarifier(BaseAgent):

    def __init__(self, system_prompt: str = SYSTEM_PROMPT_CLARIFICATION_NODE, llm_call: callable = llm_call,
                 context: dict = None):
        super().__init__(system_prompt, llm_call, context)
        self._system_prompt = system_prompt
        self._llm_call = llm_call
        self._messages = context["messages"] if context else []
        self._agent_results = context["agent_results"] if context else []
        self._clarification_num_iterations = CLARIFICATION_NUM_ITERATIONS

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




    def clarify(self, user_input: str) -> dict:
        if self._clarification_num_iterations <= 0:
            return {"is_bpmn_request": True, "reason": "Clarification limit reached."}
        final_prompt = self._build_final_prompt(user_input)
        response = self.llm_call(user_input, final_prompt)
        response = self._process_response(response)
        return response


class Verifer(BaseAgent):

    def __init__(self, system_prompt: str = SYSTEM_PROMPT_VERIFICATION_NODE, llm_call: callable = llm_call,
                 context: dict = None):
        super().__init__(system_prompt, llm_call, context)
        self._system_prompt = system_prompt
        self._llm_call = llm_call
        self._messages = context["messages"] if context else []
        self._agent_results = context["agent_results"] if context else []

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

    def verify(self, user_input: str) -> dict:
        final_prompt = self._build_final_prompt(user_input)
        response = self.llm_call(user_input, final_prompt)
        response = self._process_response(response)
        return response



class Generator(BaseAgent):

    def __init__(self, system_prompt: str = SYSTEM_PROMPT_GENERATION_NODE, llm_call: callable = llm_call,
                 context: dict = None):
        super().__init__(system_prompt, llm_call, context)
        self._system_prompt = system_prompt
        self._llm_call = llm_call
        self._messages = context["messages"] if context else []
        self._agent_results = context["agent_results"] if context else []

    def _build_final_prompt(self, user_input: str) -> str:
        raise NotImplementedError("This method is not implemented for the Generator class.")