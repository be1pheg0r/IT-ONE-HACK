from graphviz import Digraph
from IPython.display import Image, display
from src.utilities.llm_module.states import generation
from src.utilities.llm_module.agents import CLIENT
import random
import pandas as pd
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

import graphviz
from src.utilities.llm_module.llm_constants import X6_CANVAS_SHAPE

def visualize_bpmn_graph(data, name: str):
    # Конвертируем пиксели в дюймы (Graphviz работает в дюймах, 1 дюйм = 72 пикселя)
    width_inch = X6_CANVAS_SHAPE[0] / 72
    height_inch = X6_CANVAS_SHAPE[1] / 72

    dot = graphviz.Digraph(
        format='png',
        engine='dot',
        graph_attr={
            'rankdir': 'LR',
            'size': f'{width_inch},{height_inch}!',
            'dpi': '150',
            'nodesep': '0.5',
            'ranksep': '0.75'
        }
    )

    for item in data:
        if item['shape'] == 'bpmn-edge':
            continue
        node_id = item['id']
        label = item['label']
        shape = 'ellipse' if item['shape'] in ['start', 'end'] else 'box'
        dot.node(
            str(node_id),
            label=label,
            shape=shape,
            width=str(item.get('width', 1.5) / 72),
            height=str(item.get('height', 1.0) / 72)
        )

    for item in data:
        if item['shape'] == 'bpmn-edge':
            dot.edge(str(item['source']), str(item['target']))

    dot.render(name, format="png", cleanup=True)
    return dot



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


import uuid
import langid

from llm_constants import MISTRAL_API_KEY, MODELS
from mistralai import Mistral
from mistralai.models import SystemMessage
import logging
from typing import List, Optional


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

# df = generate_prompt_dataframe(200)
# df.to_csv("../files/test_data/data.csv")

# df = pd.read_csv("../../../files/test_data/data.csv").drop(["Unnamed: 0"], axis=1)
#
# df = df[df["query"].str.contains("Sure, here's a prompt for you:")]
# print(df["query"])

