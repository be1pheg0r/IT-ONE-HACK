from graphviz import Digraph
from IPython.display import Image, display
from app.llm_module.states import generation
from app.llm_module.agents import CLIENT
import random
from mistralai import Mistral
from mistralai.models import SystemMessage
import pandas as pd
from app.llm_module.llm_constants import PROMPTS, MISTRAL_API_KEY, MODELS
from app.llm_module.src.markup_to_x6 import x6_layout
from tqdm import tqdm

import logging


def render_langgraph_graphviz(compiled_graph, filename="langgraph_graph", format="png", show_in_notebook=True):
    dot = Digraph(format=format)

    # Цвета для разных типов узлов (можно расширить)
    type_colors = {
        "Clarifier": "#D1F2EB",
        "Verifier": "#FCF3CF",
        "X6Processor": "#FADBD8",
        "ToolNode": "#E8DAEF",  # пример на случай, если ты используешь tool-like узлы
    }

    # Узлы
    for node_id, node_info in compiled_graph.get_graph().nodes.items():
        class_name = ""
        if hasattr(node_info, "node"):
            class_name = node_info.node.__class__.__name__
        label = f"<<b>{node_id}</b><br/>{class_name}>"
        fillcolor = type_colors.get(class_name, "#f2f0ff")
        dot.node(node_id, label=label, shape="box", style="filled,rounded", fillcolor=fillcolor, fontname="Courier New")

    # Старт/конец
    if hasattr(compiled_graph, "start") and compiled_graph.start:
        dot.node("__start__", "Start", shape="circle", style="filled", fillcolor="#D6EAF8", fontname="Courier New")
        dot.edge("__start__", compiled_graph.start, penwidth="2")

    if hasattr(compiled_graph, "end") and compiled_graph.end:
        dot.node("__end__", "End", shape="doublecircle", style="filled", fillcolor="#D7BDE2", fontname="Courier New")
        dot.edge(compiled_graph.end, "__end__", penwidth="2")

    # Рёбра
    for edge in compiled_graph.get_graph().edges:
        src = edge.source
        dest = edge.target
        conditional = getattr(edge, "conditional", False)
        style = "dashed" if conditional else "bold"
        color = "#A569BD" if conditional else "#34495E"
        dot.edge(src, dest, style=style, color=color, penwidth="2")

    # Рендер
    output_path = dot.render(filename, cleanup=True)
    print(f"Graph saved as {output_path}")

    if show_in_notebook:
        display(Image(filename=output_path))


def visualize_bpmn_graph(nodes_and_edges, filename="bpmn_graph", format="png", show=True):
    dot = Digraph(format=format)

    # Маппинг форм BPMN на формы Graphviz
    shape_map = {
        "start": "circle",
        "end": "doublecircle",
        "task": "box",
        "gateway": "diamond"
    }

    # Отдельно собираем узлы и рёбра
    nodes = []
    edges = []
    for i, element in enumerate(nodes_and_edges):
        if element["shape"] == "bpmn-edge":
            edges.append(element)
        else:
            nodes.append(element)

    # Добавляем узлы
    for node in nodes:
        shape = shape_map.get(node["shape"], "box")
        label = node.get("label", str(node["id"]))
        dot.node(str(node["id"]), label=label, shape=shape, style="filled", fillcolor="#f0f0ff")

    # Добавляем рёбра
    for edge in edges:
        dot.edge(str(edge["source"]), str(edge["target"]))

    output_path = dot.render(filename, cleanup=True)
    print(f"Graph saved to {output_path}")

    if show:
        display(Image(filename=output_path))

    return output_path


# Твоя функция вызова
def mistral_call(messages: list[dict], system_prompt: str) -> str:
    passed = False
    while not passed:
        try:
            response = CLIENT.chat.complete(
                model=MODELS["mistral"],
                messages=[SystemMessage(content=system_prompt)] + messages,
                safe_prompt=True
            )
            return response.choices[0].message.content
        except:
            passed = False


languages = ["English", "Spanish", "German", "French", "Russian", "Chinese", "Japanese"]
non_bpmn_topics = ["network setup", "vacation planning", "cooking recipes", "sports results", "router password",
                   "movie recommendations"]


def generate_prompt_dataframe(n=100):
    bpmn_ratio = 0.8
    n_bpmn = int(n * bpmn_ratio)
    n_non_bpmn = n - n_bpmn

    data = []

    # 1. BPMN-запросы
    for _ in tqdm(range(n_bpmn), desc="Generating BPMN prompts"):
        lang = random.choice(languages)
        bpmn_prompt_type = random.choice([
            f"Generate a user request in {lang} that asks to create a BPMN diagram for a specific business generation.",
            f"Generate a detailed user query in {lang} describing a business generation and requesting a BPMN diagram.",
            f"Write a short message in {lang} asking for a BPMN diagram generation based on a generation description."
        ])

        messages = [{"role": "user", "content": "Okay, give me the prompt"}]
        prompt = mistral_call(messages, bpmn_prompt_type)

        data.append({
            "query": prompt,
            "language": lang,
            "related_bpmn": True
        })

    # 2. Нерелевантные запросы
    for _ in tqdm(range(n_non_bpmn), desc="Generating unrelated prompts"):
        lang = random.choice(languages)
        topic = random.choice(non_bpmn_topics)
        system_prompt = f"Generate a short user query in {lang} on the topic: {topic}. This query should NOT be about BPMN or business processes."

        messages = [{"role": "user", "content": "Okay, give me the prompt"}]
        prompt = mistral_call(messages, system_prompt)

        data.append({
            "query": prompt,
            "language": lang,
            "related_bpmn": False
        })

    random.shuffle(data)  # Перемешиваем, чтобы не было сгруппировано
    return pd.DataFrame(data)


import json
import uuid
from abc import ABC
from typing import Callable, List, Optional, Dict
from mistralai.models import SystemMessage, UserMessage, AssistantMessage
from app.utils.logger import setup_logger
import langid

logger = setup_logger("BaseAgent")
from app.llm_module.base_agent import BaseAgent
from app.llm_module.llm_constants import PROMPTS, MISTRAL_API_KEY, MODELS
from mistralai import Mistral
from mistralai.models import SystemMessage
import langid
import logging
from app.utils.logger import setup_logger
import json
from typing import List, Optional

logger = setup_logger("BaseAgent", logging.DEBUG)

CLIENT = Mistral(api_key=MISTRAL_API_KEY)


def mistral_call(messages: List[dict], system_prompt: str) -> str:
    passed = False
    while not passed:
        try:
            response = CLIENT.chat.complete(
                model=MODELS["mistral"],
                messages=messages,
                safe_prompt=True
            )
            return response.choices[0].message.content
        except:
            passed = False

