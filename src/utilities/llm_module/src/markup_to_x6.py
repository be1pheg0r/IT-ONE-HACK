from src.utilities.llm_module.llm_constants import X6_CANVAS_SHAPE
import networkx as nx
import math


def x6_layout(graph: dict | list[dict]):
    G = nx.DiGraph()

    for node in graph["nodes"]:
        G.add_node(node["id"], **node)

    for edge in graph["edges"]:
        G.add_edge(edge["source"], edge["target"], **edge)

    # Собственная реализация размещения слева направо
    pos = {}
    levels = {}

    # Определяем уровни для каждого узла (топологическая сортировка)
    for node in nx.topological_sort(G):
        if not list(G.predecessors(node)):
            levels[node] = 0
        else:
            levels[node] = max(levels[p] for p in G.predecessors(node)) + 1

    # Группируем узлы по уровням
    level_groups = {}
    for node, level in levels.items():
        level_groups.setdefault(level, []).append(node)

    # Распределяем узлы по уровням и позициям
    max_level = max(levels.values()) if levels else 0
    vertical_spacing = 100
    horizontal_spacing = 150

    for level, nodes in level_groups.items():
        # Сортируем узлы в пределах уровня для согласованности
        nodes_sorted = sorted(nodes)
        n_nodes = len(nodes_sorted)
        for i, node in enumerate(nodes_sorted):
            # Равномерное распределение по вертикали
            y = (i - n_nodes/2) * vertical_spacing
            x = level * horizontal_spacing
            pos[node] = (x, y)

    shape_sizes_norm = {
        "start": (1.0, 1.0),
        "end": (1.0, 1.0),
        "event": (1.0, 1.0),
        "task": (1.0, 1.0),
        "gateway": (1.4, 1.4),
        "activity": (2.5, 1.5)
    }

    max_width, max_height = X6_CANVAS_SHAPE

    # Получим позиции и определим габариты layout-а
    x_coords = [x for x, _ in pos.values()]
    y_coords = [y for _, y in pos.values()]
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)

    layout_width = max_x - min_x or 1
    layout_height = max_y - min_y or 1

    # Вычислим базовые размеры с запасом
    n_nodes = len(G.nodes)
    estimated_columns = int(n_nodes ** 0.5)
    estimated_rows = (n_nodes + estimated_columns - 1) // estimated_columns

    # Место под самый крупный узел (масштабируем позже)
    max_norm_width = max(w for w, _ in shape_sizes_norm.values())
    max_norm_height = max(h for _, h in shape_sizes_norm.values())

    base_width = max_width / (layout_width + max_norm_width + 1)
    base_height = max_height / (layout_height + max_norm_height + 1)

    x6_nodes = []
    x6_edges = []

    for node_id, (x, y) in pos.items():
        node_data = G.nodes[node_id]
        shape = node_data.get("shape", "activity")
        norm_width, norm_height = shape_sizes_norm.get(shape, (2.5, 1.5))

        width = base_width * norm_width
        height = base_height * norm_height

        # Смещаем и нормализуем позицию
        scaled_x = ((x - min_x) / layout_width) * (max_width - width)
        scaled_y = ((y - min_y) / layout_height) * (max_height - height)

        node_entry = {
            "id": node_id,
            "shape": shape,
            "width": round(width, 2),
            "height": round(height, 2),
            "position": {
                "x": round(scaled_x, 2),
                "y": round(scaled_y, 2)
            }
        }

        if "label" in node_data:
            node_entry["label"] = node_data["label"]

        if shape == "event" and node_data.get("thick", False):
            node_entry["attrs"] = {
                "body": {
                    "strokeWidth": 4
                }
            }

        x6_nodes.append(node_entry)

    for i, (src, tgt) in enumerate(G.edges()):
        x6_edges.append({
            "id": i + 1 + len(x6_nodes),
            "shape": "bpmn-edge",
            "source": src,
            "target": tgt
        })

    return x6_nodes + x6_edges
