import json
import os
from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.checkpoint import MemorySaver
from dotenv import load_dotenv
from abc import ABC

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
CLIENT = Mistral(api_key=MISTRAL_API_KEY)
MODEL = "ministral-8b-latest"

SYSTEM_PROMPT_VERIFICATION_NODE = """
You are an expert in BPMN diagrams. Your task is to determine if the user's request is an intention to generate a Business Process Model and Notation (BPMN) diagram. Please respond strictly in the following JSON format:

{"is_bpmn_request": true/false, 
"reason": "explanation"}

If the request is related to generating a BPMN diagram, set "is_bpmn_request" to true and provide a brief explanation in the "reason" field. If it's not related, set "is_bpmn_request" to false and provide a varied, polite refusal message such as:
- "Извините, но я не могу с этим помочь."
- "К сожалению, я не могу обработать такой запрос."
- "Извините, это не связано с BPMN, я не могу помочь в данном случае."
- "Это выходит за рамки моих возможностей. Я не могу помочь с этим запросом."

The response should be in Russian.
"""

SYSTEM_PROMPT_CLARIFICATION_NODE = """
You are an expert in BPMN diagrams. Your task is to clarify the user's request for generating a Business Process Model and Notation (BPMN) diagram. Please respond strictly in the following JSON format:

{"clarification_needed": true/false,
"clarification": "question or explanation"}

Only if the user's request is vague, extremely short, or lacks any reference to a clear business process (for example, just saying 'make a diagram' or something similarly ambiguous), set "clarification_needed" to true. In that case, provide a brief clarification question like: "Could you specify which process you'd like to model in the BPMN diagram?" or "Can you describe the steps involved in the process you want to visualize?" 

If the request clearly indicates the intention to generate a BPMN diagram with adequate context (e.g., "make a diagram for the order processing in an electronics store" or "show me the steps for inventory management in a warehouse"), set "clarification_needed" to false, as no clarification is needed.

The response should be in Russian.
"""

SYSTEM_PROMPT_GENERATION_NODE = """
Generate ONLY Python code that uses the 'bpmn_python' library to create a BPMN diagram based on the following description: "{user_input}". 
The generated code must be executable and capable of directly implementing the BPMN diagram. 
Include NO explanations, comments, or extra text — only the Python code itself. Ensure the code is efficient and follows 
best practices for creating BPMN diagrams with the 'bpmn_python' library.
"""


def llm_call(user_prompt: str, system_prompt: str) -> str:
    response = CLIENT.chat.complete(
        model=MODEL,
        messages=[
            SystemMessage(content=system_prompt),
            UserMessage(content=user_prompt)
        ],
        safe_prompt=True
    )
    return response.choices[0].message.content


class BaseNode(ABC):
    def __init__(self, system_prompt: str, llm_call: callable = llm_call):
        self.system_prompt = system_prompt
        self.llm_call = llm_call

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


class VerificationNode(BaseNode):
    def __init__(self, system_prompt: str = SYSTEM_PROMPT_VERIFICATION_NODE, llm_call: callable = llm_call):
        super().__init__(system_prompt, llm_call)

    def verify(self, user_input: str) -> dict:
        response = self.llm_call(user_input, self.system_prompt)
        return self._process_response(response)


class ClarificationNode(BaseNode):
    def __init__(self, system_prompt: str = SYSTEM_PROMPT_CLARIFICATION_NODE, llm_call: callable = llm_call):
        super().__init__(system_prompt, llm_call)

    def clarify(self, user_input: str) -> dict:
        response = self.llm_call(user_input, self.system_prompt)
        return self._process_response(response)


class GenerationNode(BaseNode):
    def __init__(self, system_prompt: str = SYSTEM_PROMPT_GENERATION_NODE, llm_call: callable = llm_call):
        super().__init__(system_prompt, llm_call)

    def generate(self, user_input: str) -> dict:
        response = self.llm_call(user_input, self.system_prompt)
        return self._process_response(response)
