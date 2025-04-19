from src.utilities.llm_module.llm_constants import X6_CANVAS_SHAPE
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from typing import List

import warnings

warnings.filterwarnings("ignore")


def x6_layout(graph: dict | List[dict]):
    G = nx.DiGraph()

    for node in graph["nodes"]:
        G.add_node(node["id"], **node)

    for edge in graph["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)

    pos = graphviz_layout(G, prog="dot", args="-Grankdir=LR")

    max_width, max_height = X6_CANVAS_SHAPE

    max_x = max(x for x, _ in pos.values())
    max_y = max(y for _, y in pos.values())
    x_scale = max_width / (max_x + 1)
    y_scale = max_height / (max_y + 1)

    shape_sizes = {
        "event": (40, 40),
        "gateway": (55, 55),
        "activity": (100, 60)
    }

    x6_nodes = []
    x6_edges = []

    for node_id, (x, y) in pos.items():
        node_data = G.nodes[node_id]
        shape = node_data.get("shape", "activity")
        width, height = shape_sizes.get(shape, shape_sizes["activity"])
        label = node_data.get("label", node_id)

        scaled_x = round(x * x_scale, 2)
        scaled_y = round(y * y_scale, 2)

        node_entry = {
            "id": node_id,
            "shape": shape,
            "width": width * x_scale,
            "height": height * y_scale,
            "position": {
                "x": scaled_x,
                "y": scaled_y
            }
        }

        if label:
            node_entry["label"] = label

        if shape == "event" and node_data.get("thick", False):
            node_entry["attrs"] = {
                "body": {
                    "strokeWidth": 4
                }
            }

        x6_nodes.append(node_entry)

    for i, (src, tgt) in enumerate(G.edges()):
        x6_edges.append({
            "id": i+1 + len(x6_nodes),
            "shape": "bpmn-edge",
            "source": src,
            "target": tgt
        })

    return x6_nodes + x6_edges
