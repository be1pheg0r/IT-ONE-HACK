import re
import json
from app.mcp.llm_constants import X6_CANVAS_SHAPE
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt

import warnings

warnings.filterwarnings("ignore")



def x6_layout(graph: dict):
    G = nx.DiGraph()
    for node in graph["nodes"]:
        G.add_node(node["id"], **node)

    for edge in graph["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)

    pos = graphviz_layout(G, prog="dot")

    max_width, max_height = X6_CANVAS_SHAPE
    x_scale = max_width / (max(x for x, _ in pos.values()) + 1)
    y_scale = max_height / (max(y for _, y in pos.values()) + 1)

    x6_nodes = []
    x6_edges = []

    for node_id, (x, y) in pos.items():
        node_data = G.nodes[node_id]
        shape = node_data.get("shape", "activity")
        width = node_data.get("width", 100)
        height = node_data.get("height", 60)
        label = node_data.get("label", node_id)

        node_entry = {
            "id": node_id,
            "shape": shape,
            "width": width,
            "height": height,
            "position": {
                "x": round(x * x_scale, 2),
                "y": round(y * y_scale, 2)
            }
        }

        if label:
            node_entry["label"] = label
        if shape == "event":
            node_entry["width"] = 40
            node_entry["height"] = 40
        elif shape == "gateway":
            node_entry["width"] = 55
            node_entry["height"] = 55

        if shape == "event" and node_data.get("thick", False):
            node_entry["attrs"] = {
                "body": {
                    "strokeWidth": 4
                }
            }

        x6_nodes.append(node_entry)

    for i, (src, tgt) in enumerate(G.edges()):
        x6_edges.append({
            "id": f"{i+1 + len(x6_nodes)}",
            "shape": "bpmn-edge",
            "source": src,
            "target": tgt
        })

    return x6_nodes + x6_edges