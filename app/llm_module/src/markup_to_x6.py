from app.llm_module.llm_constants import X6_CANVAS_SHAPE
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

import warnings

warnings.filterwarnings("ignore")


def x6_layout(graph: dict):
    # Инициализация направленного графа
    G = nx.DiGraph()

    # Добавляем узлы в граф с их атрибутами
    for node in graph["nodes"]:
        G.add_node(node["id"], **node)

    # Добавляем рёбра в граф
    for edge in graph["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)

    # Получаем расположение узлов с аргументом для горизонтальной ориентации
    pos = graphviz_layout(G, prog="dot", args="-Grankdir=LR")

    # Получаем размеры канваса для масштабирования
    max_width, max_height = X6_CANVAS_SHAPE

    # Рассчитываем коэффициенты масштабирования для осей
    max_x = max(x for x, _ in pos.values())
    max_y = max(y for _, y in pos.values())
    x_scale = max_width / (max_x + 1)
    y_scale = max_height / (max_y + 1)

    # Задаём базовые размеры для различных форм узлов
    shape_sizes = {
        "event": (40, 40),      # Размер для "event"
        "gateway": (55, 55),    # Размер для "gateway"
        "activity": (100, 60)   # Размер для "activity"
    }

    x6_nodes = []
    x6_edges = []

    # Обрабатываем узлы для масштабирования их позиций и размеров
    for node_id, (x, y) in pos.items():
        node_data = G.nodes[node_id]
        shape = node_data.get("shape", "activity")
        width, height = shape_sizes.get(shape, shape_sizes["activity"])  # Используем значение по умолчанию
        label = node_data.get("label", node_id)

        # Масштабируем позиции узлов по осям x и y
        scaled_x = round(x * x_scale, 2)
        scaled_y = round(y * y_scale, 2)

        # Добавляем информацию об узле с масштабированными значениями
        node_entry = {
            "id": node_id,
            "shape": shape,
            "width": width * x_scale,   # Масштабируем ширину
            "height": height * y_scale, # Масштабируем высоту
            "position": {
                "x": scaled_x,
                "y": scaled_y
            }
        }

        # Если у узла есть метка, добавляем её
        if label:
            node_entry["label"] = label

        # Добавляем дополнительные атрибуты для определённых форм
        if shape == "event" and node_data.get("thick", False):
            node_entry["attrs"] = {
                "body": {
                    "strokeWidth": 4  # Толще линия для event
                }
            }

        x6_nodes.append(node_entry)

    # Обрабатываем рёбра
    for i, (src, tgt) in enumerate(G.edges()):
        x6_edges.append({
            "id": f"{i+1 + len(x6_nodes)}",  # Уникальный ID для рёбер
            "shape": "bpmn-edge",             # Форма рёбер
            "source": src,                    # Источник рёбер
            "target": tgt                     # Цель рёбер
        })

    return x6_nodes + x6_edges
