import pytest

from db.index.hnsw.hnsx_index import HNSWIndex, HNSWNode, SearchState
from db.record.record_id import RecordID


@pytest.fixture
def basic_nodes():
    apple_fruit = HNSWNode([0.1, 0.2, 0.3], RecordID(1, 2))
    apple_pc = HNSWNode([0.9, 0.1, 0.5], RecordID(3, 4))
    return apple_fruit, apple_pc


@pytest.fixture
def apple_and_orange_query():
    return [0.1, 0.2, 0.2]


# HNSWNode のテスト
def test_get_hnsw_node(apple_and_orange_query):
    record_id = RecordID(1, 2)
    node = HNSWNode(apple_and_orange_query, record_id)

    assert node.vector == apple_and_orange_query
    assert node.record_id == record_id
    assert node.get_neighbors(0) == []


def test_set_hnsw_node(apple_and_orange_query):
    record_id = RecordID(1, 2)
    node = HNSWNode(apple_and_orange_query, record_id)

    neighbors_layer_0 = [HNSWNode([0.4, 0.5, 0.6], RecordID(3, 4))]

    node.set_neighbors(0, neighbors_layer_0)

    assert node.get_neighbors(0) == neighbors_layer_0
    assert node.get_neighbors(1) == []  # 存在しないレイヤ


# SearchState のテスト
def test_search_state_initialization(apple_and_orange_query):
    entry_points = [HNSWNode([0.1, 0.2, 0.3], RecordID(1, 2))]
    state = SearchState(entry_points, apple_and_orange_query)

    assert state.visited == {id(entry_points[0])}
    assert len(state.candidates) == 1
    assert len(state.nearest_set) == 1


def test_search_state_sorted(apple_and_orange_query, basic_nodes):
    apple_fruit, apple_pc = basic_nodes

    state = SearchState([apple_fruit, apple_pc], apple_and_orange_query)

    assert state.candidates[0][1] == apple_fruit
    assert state.candidates[1][1] == apple_pc
    assert state.nearest_set[0][1] == apple_fruit


def test_search_layer_no_candidates(apple_and_orange_query):
    apple_fruit = HNSWNode([0.1, 0.2, 0.3], RecordID(1, 2))
    apple_and_orange_query = [0.1, 0.2, 0.3]
    state = SearchState([apple_fruit], apple_and_orange_query)

    result = state.search_layer(apple_and_orange_query, ef=1, layer=0)

    assert result[0][1] == apple_fruit
    assert len(result) == 1


def test_search_layer_explores_neighbors(basic_nodes, apple_and_orange_query):
    apple_fruit, apple_pc = basic_nodes

    state = SearchState([apple_fruit], apple_and_orange_query)
    apple_fruit.set_neighbors(0, [apple_pc])

    result = state.search_layer(apple_and_orange_query, ef=2, layer=0)

    assert result[0][1] == apple_fruit
    assert result[1][1] == apple_pc


def test_update_with_visited_neighbors(basic_nodes, apple_and_orange_query):
    apple_fruit, apple_pc = basic_nodes

    state = SearchState([apple_fruit], apple_and_orange_query)
    apple_fruit.set_neighbors(0, [apple_pc])
    state.visited.add(id(apple_pc))

    result = state.search_layer(apple_and_orange_query, ef=2, layer=0)

    assert len(result) == 1
    assert result[0][1] == apple_fruit


def test_update_with_not_visited_neighbors(apple_and_orange_query, basic_nodes):
    apple_fruit, apple_pc = basic_nodes

    state = SearchState([apple_fruit], apple_and_orange_query)
    apple_fruit.set_neighbors(0, [apple_pc])

    result = state.search_layer(apple_and_orange_query, ef=2, layer=0)

    assert len(result) == 2
    assert result[0][1] == apple_fruit
    assert result[1][1] == apple_pc


def test_insert_hnsw_node(apple_and_orange_query):
    # HNSWNode の挿入テスト
    record_id = RecordID(1, 2)

    index = HNSWIndex()
    index.insert(apple_and_orange_query, record_id)

    assert len(index.nodes) == 1
    assert index.entry_point is not None
    assert index.entry_point.record_id == record_id


def test_insert_multiple_nodes(basic_nodes):

    apple_fruit, apple_pc = basic_nodes

    index = HNSWIndex()
    index.insert(apple_fruit.vector, apple_fruit.record_id)
    index.insert(apple_pc.vector, apple_pc.record_id)

    assert len(index.nodes) == 2
    assert index.entry_point is not None
    assert index.entry_point.record_id == apple_fruit.record_id or index.entry_point.record_id == apple_pc.record_id


def test_search(apple_and_orange_query, basic_nodes):
    apple_fruit, apple_pc = basic_nodes

    index = HNSWIndex()
    index.insert(apple_fruit.vector, apple_fruit.record_id)
    index.insert(apple_pc.vector, apple_pc.record_id)

    results = index.search(apple_and_orange_query, k=2)

    assert len(results) == 2
    assert results[0] == RecordID(1, 2)
    assert results[1] == RecordID(3, 4)
