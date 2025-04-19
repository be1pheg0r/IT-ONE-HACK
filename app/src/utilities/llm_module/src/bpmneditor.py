from typing import *
from app.utils.logger import setup_logger
from app.llm_module.llm_constants import X6_CANVAS_SHAPE
import random

logger = setup_logger("BPMNEditor")

class BPMNEditor:
    def __init__(self, bpmn_data: List[Dict]):
        self.bpmn = bpmn_data
        self.nodes = []
        self.edges = []

        # Преобразование всех id в целые числа
        for i, item in enumerate(self.bpmn):
            self.bpmn[i]["id"] = int(item["id"])  # <-- преобразуем ID в int
            if item["shape"] == "bpmn-edge":
                self.edges.append(self.bpmn[i])
            else:
                self.nodes.append(self.bpmn[i])

        # Использование числовых ID в словаре
        self.id_dict = {item["id"]: item for item in self.bpmn}
        logger.info("BPMNEditor initialized with %d elements.", len(bpmn_data))

    def _generate_id(self) -> int:
        # Генерация нового ID, который будет целым числом
        existing_ids = [k for k in self.id_dict.keys()]
        new_id = max(existing_ids, default=0) + 1
        logger.debug("Generated new ID: %d", new_id)
        return new_id

    def _is_valid_position(self, x: int, y: int) -> bool:
        valid = 0 <= x <= X6_CANVAS_SHAPE[0] and 0 <= y <= X6_CANVAS_SHAPE[1]
        logger.debug("Position (%d, %d) valid: %s", x, y, valid)
        return valid

    def add_node(self, shape: str, position: Tuple[int, int], label: str = None,
                 width: int = None, height: int = None) -> Dict:
        x, y = position
        if not self._is_valid_position(x, y):
            logger.error("Invalid position: (%d, %d)", x, y)
            raise ValueError("Position is out of bounds.")

        default_sizes = {
            "event": (40, 40),
            "gateway": (55, 55),
            "activity": (100, 60)
        }
        width = width or default_sizes.get(shape, (80, 50))[0]
        height = height or default_sizes.get(shape, (80, 50))[1]

        node = {
            "id": self._generate_id(),  # ID теперь целое число
            "shape": shape,
            "width": width,
            "height": height,
            "position": {"x": x, "y": y}
        }

        if label:
            node["label"] = label

        self.bpmn.append(node)
        self.id_dict[node["id"]] = node
        logger.info("Added node: %s", node)
        return node

    def get_previous_next(self, node_id: int) -> Tuple[Optional[int], Optional[int]]:
        previous_node_id = None
        next_node_id = None

        # Перебор всех рёбер, чтобы найти предыдущий и следующий узел для заданного node_id
        for edge in self.bpmn:
            if edge["shape"] == "bpmn-edge":
                if edge.get("target") == node_id:
                    previous_node_id = edge.get("source")
                elif edge.get("source") == node_id:
                    next_node_id = edge.get("target")

        logger.debug("For node %d: previous = %s, next = %s", node_id, previous_node_id, next_node_id)
        return previous_node_id, next_node_id

    def remove_node(self, label: str) -> None:
        # Найдем узел с заданным лейблом
        node_to_remove = None
        for node in self.bpmn:
            if node.get("label") == label:
                node_to_remove = node
                break  # Прерываем цикл после нахождения первого узла с таким лейблом

        if not node_to_remove:
            logger.error(f"Node with label '{label}' not found.")
            return

        node_id = node_to_remove["id"]
        prev_id, next_id = self.get_previous_next(node_id)

        logger.info(f"bpmn before removing node with label={label}: {self.bpmn}\n ")

        # Считаем количество рёбер, идущих к узлу и от узла
        incoming_edges = [edge for edge in self.bpmn if edge.get("target") == node_id]
        outgoing_edges = [edge for edge in self.bpmn if edge.get("source") == node_id]

        # Обработаем случаи в зависимости от количества рёбер
        if len(incoming_edges) > 1 and len(outgoing_edges) == 1:
            # Если к узлу идет несколько рёбер, а от узла идет одно ребро, перенаправляем все рёбра к следующей ноде
            for edge in incoming_edges:
                self.add_edge(edge["source"], next_id)
            logger.info(f"All incoming edges redirected to node {next_id}.")

        elif len(incoming_edges) == 1 and len(outgoing_edges) > 1:
            # Если к узлу идет одно ребро, а от узла идет несколько рёбер, перенаправляем все рёбра, идущие к удаляемому узлу, ко всем следующим нодам
            for edge in incoming_edges:
                for next_edge in outgoing_edges:
                    self.add_edge(edge["source"], next_edge["target"])
            logger.info(f"All incoming edges redirected to all following nodes.")

        elif len(incoming_edges) > 1 and len(outgoing_edges) > 1:
            # Если к узлу и от узла идут несколько рёбер, распределяем рёбра случайным образом
            all_next_nodes = [next_id]
            for edge in outgoing_edges:
                if edge["target"] != next_id:
                    all_next_nodes.append(edge["target"])

            random.shuffle(all_next_nodes)

            # Перенаправляем входящие рёбра на все следующие ноды
            for edge in incoming_edges:
                for next_node in all_next_nodes:
                    self.add_edge(edge["source"], next_node)

            # Перенаправляем исходящие рёбра
            for edge in outgoing_edges:
                for next_node in all_next_nodes:
                    self.add_edge(edge["source"], next_node)

            logger.info(f"Edges randomly redistributed to following nodes: {all_next_nodes}")

        # Удаление всех рёбер, где node_id является источником или целью
        self.bpmn = [item for item in self.bpmn if not (
                (item.get("shape") == "bpmn-edge") and
                (item.get("source") == node_id or item.get("target") == node_id)
        )]

        # Удаление самого узла из диаграммы
        self.bpmn = [item for item in self.bpmn if item.get("id") != node_id]

        # Удаление самого узла из вспомогательного словаря
        if node_id in self.id_dict:
            self.id_dict.pop(node_id)

        logger.info(f"bpmn after removing node with label={label}: {self.bpmn}\n ")

    def add_edge(self, source_id: int, target_id: int) -> Dict:
        node_ids = {item["id"] for item in self.bpmn}
        if source_id not in node_ids or target_id not in node_ids:
            logger.error("Invalid edge: source (%d) or target (%d) not found.", source_id, target_id)
            raise ValueError("Source or target node ID not found.")

        edge = {
            "id": self._generate_id(),  # ID рёбер теперь тоже целое число
            "shape": "bpmn-edge",
            "source": source_id,
            "target": target_id
        }

        self.bpmn.append(edge)
        self.id_dict[edge["id"]] = edge
        logger.info("Added edge: %s", edge)
        return edge


from app.src.utilities.llm_module.test import visualize_bpmn_graph
import json

with open('../../../../files/json/bpmn.json', 'r', encoding='utf-8') as f:
    bpmn = json.load(f)

visualize_bpmn_graph(bpmn, filename='before')

print(bpmn)
editor = BPMNEditor(bpmn)
visualize_bpmn_graph(editor.bpmn, filename='after')
print(editor.bpmn)


print(editor.bpmn == bpmn)
