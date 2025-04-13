import os
from dotenv import load_dotenv

load_dotenv()

system_verification_prompt = """
You are an expert in BPMN diagrams. Your task is to determine if the user's request is an intention to generate a Business Process Model and Notation (BPMN) diagram. Please respond strictly in the following JSON format:

{"is_bpmn_request": true/false, 
"reason": "explanation"}

If the request is related to generating a BPMN diagram, set "is_bpmn_request" to true and provide a brief explanation in the "reason" field. If it's not related, set "is_bpmn_request" to false and provide a varied, polite refusal message such as:
-"I'm sorry, but I cannot assist with that request."
-"Unfortunately, that request does not pertain to BPMN diagram generation."
The response should be in user's language.
"""

system_clarification_node = """
You are an expert in BPMN diagrams. Your task is to clarify the user's request for generating a Business Process Model and Notation (BPMN) diagram. Please respond strictly in the following JSON format:

{"clarification_needed": true/false,
"clarification": "question or explanation"}

Only if the user's request is vague, extremely short, or lacks any reference to a clear business process (for example, just saying 'make a diagram' or something similarly ambiguous), set "clarification_needed" to true. In that case, provide a brief clarification question like: "Could you specify which process you'd like to model in the BPMN diagram?" or "Can you describe the steps involved in the process you want to visualize?" 

If the request clearly indicates the intention to generate a BPMN diagram with adequate context (e.g., "make a diagram for the order processing in an electronics store" or "show me the steps for inventory management in a warehouse"), set "clarification_needed" to false, as no clarification is needed.

The response should be in user's language.

Provided context: {context}
"""

preprocessing_prompt = """
Return the business process as a structured graph. Use the following JSON format:

{
  "nodes": [
    {"id": 1, "shape": "start", "type": "start_event", "label": "Start"},
    {"id": 2, "shape":  "task", "type": "task", "label": "Check application"},
    {"id": 3, "shape":  "gateway", "type": "gateway", "label": "Approved?"},
    {"id": 4, "shape":  "task", "type": "task", "label": "Notify applicant"},
    {"id": 5, "shape":  "end", "type": "end_event", "label": "End"}
  ],
  "edges": [
    {"source": 1, "target": 2},
    {"source": 2, "target": 3},
    {"source": 3, "target": 4},
    {"source": 3, "target": 5},
    {"source": 4, "target": 5}
  ]
}

possible shapes = ["start", "task", "gateway", "end"]

Text and labels must be in the same language as the user request.
Return only the JSON object.

Provided context: {context}
"""

system_bpmn_markup_prompt = "nothing)"

PROMPTS = {
    "clarification": system_clarification_node,
    "verification": system_verification_prompt,
    "preprocessing": preprocessing_prompt
}
CLARIFICATION_NUM_ITERATIONS = 2

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

mistral_model = os.getenv("MISTRAL_MODEL")
MODELS ={
    "mistral": mistral_model
}

X6_CANVAS_SHAPE = [600, 600]
