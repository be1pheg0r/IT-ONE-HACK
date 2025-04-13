from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from agents import Verifier, Clarifier, Preprocessor
from llm_constants import CLARIFICATION_NUM_ITERATIONS
from services.markup_to_x6 import x6_layout
import json


class State(TypedDict):
    user_input: str
    verifier_result: dict
    clarifier_result: dict
    preprocessor_result: list
    context: dict
    clarification_num_iterations: int


def verifier_node(state: State) -> dict:
    verifier = Verifier(context=state["context"])
    verifier_result = verifier(state)
    state["verifier_result"] = verifier_result
    state["context"] = verifier.get_context()
    return state


def verifier_condition(state: State) -> str:
    if state["verifier_result"]["is_bpmn_request"] == "true":
        return "clarifier"
    return END


def clarifier_node(state: State) -> dict:
    clarifier = Clarifier(context=state["context"])
    clarifier_result = clarifier(state)
    state["clarifier_result"] = clarifier_result
    state["context"] = clarifier.get_context()
    return state


def clarifier_condition(state: State) -> str:
    if state["clarifier_result"]["clarification_needed"] == "true":
        if state["clarification_num_iterations"] > 0:
            state["clarification_num_iterations"] -= 1
            return "clarifier"
        else:
            return END
    return "verifier"


def preprocessor_node(state: State) -> dict:
    preprocessor = Preprocessor(context=state["context"])
    preprocessor_result = preprocessor(state)
    state["preprocessor_result"] = x6_layout(preprocessor_result)
    return state


graph = StateGraph(State)

graph.add_node("verifier", verifier_node)
graph.set_entry_point("verifier")
graph.add_node("clarifier", clarifier_node)
graph.add_node("preprocessor", preprocessor_node)

graph.add_conditional_edges("verifier", verifier_condition,
                            {"clarifier": "clarifier", END: END})
graph.add_conditional_edges("clarifier", clarifier_condition,
                            {"clarifier": "clarifier", "verifier": "verifier", END: END})

graph.add_edge("verifier", "preprocessor")

graph.add_edge("preprocessor", END)

built = graph.compile()

query = "Make a BPMN diagram for the order processing in an electronics store"

state = {
    "user_input": query,
    "verifier_result": {},
    "clarifier_result": {"clarification_needed": "false", "clarification": ""},
    "preprocessor_result": {},
    "context": {"messages": [], "agent_results": []},
    "clarification_num_iterations": CLARIFICATION_NUM_ITERATIONS
}


state = built.invoke(state)
print(state["preprocessor_result"])

# write results to file
import os

output_path = "../files/json/example.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

result = state["preprocessor_result"]

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print("✅ Файл сохранён по пути:", os.path.abspath(output_path))