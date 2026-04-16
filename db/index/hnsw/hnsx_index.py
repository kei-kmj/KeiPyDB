import math
import random

from db.index.vector_index import VectorIndex
from db.query.vector import Vector, cosine_distance
from db.record.record_id import RecordID

type Neighbors = list[HNSWNode]
type MultiLayerNeighbors = dict[int, Neighbors]
type NodeWithDistance = tuple[float, HNSWNode]


BASE_LAYER = 0


class HNSWNode:
    def __init__(self, vector: Vector, record_id: RecordID):
        self.vector = vector
        self.record_id = record_id
        self.neighbors: MultiLayerNeighbors = {}

    def get_neighbors(self, layer: int) -> Neighbors:
        return self.neighbors.get(layer, [])

    def set_neighbors(self, layer: int, neighbors: Neighbors) -> None:
        self.neighbors[layer] = neighbors


class SearchState:
    def __init__(self, entry_points: Neighbors, query: Vector) -> None:
        self.visited: set[int] = {id(ep) for ep in entry_points}
        self.candidates: list[NodeWithDistance] = []
        self.nearest_set: list[NodeWithDistance] = []

        for ep in entry_points:
            dist = cosine_distance(query, ep.vector)
            self.candidates.append((dist, ep))
            self.nearest_set.append((dist, ep))

        self.candidates.sort(key=lambda x: x[0])
        self.nearest_set.sort(key=lambda x: x[0])

    @classmethod
    def greedy_descend(cls, query: Vector, ep: Neighbors, from_layer: int, to_layer: int) -> Neighbors:
        for layer in range(from_layer, to_layer, -1):
            state = cls(ep, query)
            nearest_set = state.search_layer(query, ef=1, layer=layer)
            ep = [nearest_set[0][1]]
        return ep


    def search_layer(self, query: Vector, ef: int, layer: int) -> list[NodeWithDistance]:
        while self.candidates:
            current_dist, current_node = self.candidates.pop(0)

            if self.nearest_set and current_dist > self.nearest_set[-1][0]:
                break

            self.update(current_node, query, ef, layer)

        return self.nearest_set


    def update(
        self,
        current_node: HNSWNode,
        query: Vector,
        ef: int,
        layer: int,
    ) -> None:
        for neighbor in current_node.get_neighbors(layer):
            if id(neighbor) in self.visited:
                continue

            self.visited.add(id(neighbor))
            dist = cosine_distance(query, neighbor.vector)
            worst_dist = self.nearest_set[-1][0] if self.nearest_set else float("inf")

            if dist < worst_dist or len(self.nearest_set) < ef:
                self.candidates.append((dist, neighbor))
                self.candidates.sort(key=lambda x: x[0])
                self.nearest_set.append((dist, neighbor))
                self.nearest_set.sort(key=lambda x: x[0])
                if len(self.nearest_set) > ef:
                    self.nearest_set.pop()



class HNSWIndex(VectorIndex):
    def __init__(self, max_node_conn: int = 16, ef_construction: int = 200) -> None:

        self.nodes: Neighbors = []
        self.max_layer: int = BASE_LAYER
        self.max_node_conn = max_node_conn
        self.base_layer_max_conn = max_node_conn * 2
        self.ef_construction = ef_construction
        self.layer_decay = 1.0 / math.log(max_node_conn)
        self.entry_point: HNSWNode | None = None

    def _random_level(self) -> int:
        """
        新ノードのトップレイヤーをランダムに決定する（論文 eq.1）

        layer_decay = 1 / ln(max_node_conn) を掛けることで、
        max_node_connの大きさに関わらずレイヤーが適切に分散する。
        layer_decayがないとほぼ全ノードがレイヤー0にスポーンしてしまう。

        トップレイヤーが2になったノードは、レイヤー0から2まで全て存在する。
        挿入順序ではなく確率で決まるため、グラフ全体が均一に分散する。
        """
        return int(-1 * math.log(random.random()) * self.layer_decay)




    def insert(self, vector: Vector, record_id: RecordID) -> None:
        # ベクトルをHNSWインデックスに挿入するロジックをここに追加します
        new_node = HNSWNode(vector, record_id)
        top_level = self._random_level()

        # 各レイヤーの最初のノードを作成する
        if self.entry_point is None:
            self._insert_first_node_to_all_layers(new_node, top_level)
            return

        entry_point = [self.entry_point]
        max_layer = self.max_layer

        # 新ノードが存在しない上位レイヤーをgreedy降下してエントリポイントを絞り込む
        ep = SearchState.greedy_descend(vector, entry_point, max_layer, top_level)

        for layer in range(min(max_layer, top_level), -1, -1):
            state = SearchState(ep, vector)
            nearest_set = state.search_layer(vector, ef=self.ef_construction, layer=layer)
            current_layer_max_conn = self.base_layer_max_conn if layer == BASE_LAYER else self.max_node_conn
            neighbors = self._select_neighbors(nearest_set, current_layer_max_conn)

            self._link_both_neighbors(new_node, neighbors, layer, current_layer_max_conn)

            ep = [w[1] for w in nearest_set]

        self.nodes.append(new_node)
        self._update_entry_point(new_node, top_level)

    def _link_both_neighbors(
            self,
            new_node: HNSWNode,
            neighbors: Neighbors,
            layer: int,
            max_conn: int) -> None:
        for neighbor in neighbors:
            neighbor_neighbors = neighbor.get_neighbors(layer)
            neighbor_neighbors.append(new_node)

            if len(neighbor_neighbors) > max_conn:
                neighbor_distance: list[NodeWithDistance] = [
                    (cosine_distance(neighbor.vector, n.vector), n) for n in neighbor_neighbors
                ]
                neighbor.set_neighbors(layer, self._select_neighbors(neighbor_distance, max_conn))
            else:
                neighbor.set_neighbors(layer, neighbor_neighbors)

    def _update_entry_point(
            self,
            new_node: HNSWNode,
            top_level: int) -> None:
        if top_level > self.max_layer:
            self.entry_point = new_node
            self.max_layer = top_level

    def _insert_first_node_to_all_layers(
            self,
            new_node: HNSWNode,
            top_level: int) -> None:

        for layer in range(top_level + 1):
            new_node.set_neighbors(layer, [])
        self.entry_point = new_node
        self.max_layer = top_level
        self.nodes.append(new_node)

    def search(self, query: Vector, k: int) -> list[RecordID]:
        """
        エントリポイントがなければ空リストを返す
        上位レイヤーをgreedy_descendで降下
        レイヤー0でef=max(k, ef_construction)で探索
        RecordIDのリストを返す
        """

        if self.entry_point is None:
            return []

        entry_point = [self.entry_point]
        max_layer = self.max_layer

        ep = SearchState.greedy_descend(query, entry_point, max_layer, BASE_LAYER)

        ef = max(k, self.ef_construction)
        state = SearchState(ep, query)
        nearest_set = state.search_layer(query, ef, layer=BASE_LAYER)
        nearest_set.sort(key=lambda x: x[0])

        return [node.record_id for _, node in nearest_set[:k]]

    def close(self) -> None:
        pass

    @staticmethod
    def _select_neighbors(
            candidates: list[NodeWithDistance],
            connections_count: int
    ) -> Neighbors:
        sorted_candidates = sorted(candidates, key=lambda x: x[0])
        return [node for _, node in sorted_candidates[:connections_count]]
