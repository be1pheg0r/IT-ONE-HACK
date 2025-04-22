from src.utilities.llm_module.llm_constants import X6_CANVAS_SHAPE
from typing import List

import warnings

warnings.filterwarnings("ignore")

def x6_layout(graph: dict) -> List[dict]:
    max_width, max_height = X6_CANVAS_SHAPE
    padding = 50  # Отступ от краев холста

    nodes = graph["nodes"]
    edges = graph["edges"]
    n = len(nodes)

    # Определяем количество строк и колонок в сетке
    cols = max(1, round(n ** 0.5))
    rows = (n + cols - 1) // cols

    # Расстояние между центрами узлов
    grid_width = (max_width - 2 * padding) / cols
    grid_height = (max_height - 2 * padding) / rows

    result = []

    for idx, node in enumerate(nodes):
        row = idx // cols
        col = idx % cols

        # Центр каждой ячейки + padding
        x = padding + col * grid_width + grid_width / 2
        y = padding + row * grid_height + grid_height / 2

        result.append({
            "id": str(node["id"]),
            "shape": node.get("shape", "rect"),
            "width": node.get("width", 100),
            "height": node.get("height", 60),
            "position": {"x": round(x, 2), "y": round(y, 2)},
            "label": node.get("label", "")
        })

    for i, edge in enumerate(edges, start=1):
        result.append({
            "id": str(len(nodes) + i),
            "shape": "bpmn-edge",
            "source": str(edge["source"]),
            "target": str(edge["target"])
        })

    return result