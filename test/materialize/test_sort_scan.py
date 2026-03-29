import os
import shutil
import tempfile

import pytest

from db.server.keipy_db import KeiPyDB


@pytest.fixture
def test_db():
    """テスト用の新しいデータベースを作成"""
    temp_dir = tempfile.mkdtemp()
    db = KeiPyDB(temp_dir)
    tx = db.new_transaction()
    yield db, tx
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_sort_scan_single_field(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), price int)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('apple', 100)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('banana', 50)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('orange', 80)", tx)

    plan = planner.create_query_plan("SELECT name, price FROM items ORDER BY price", tx)
    scan = plan.open()

    results = []
    while scan.next():
        results.append(scan.get_int("price"))
    scan.close()

    assert results == [50, 80, 100]


def test_sort_scan_string_field(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), price int)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('banana', 50)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('apple', 100)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('orange', 80)", tx)

    plan = planner.create_query_plan("SELECT name FROM items ORDER BY name", tx)
    scan = plan.open()

    results = []
    while scan.next():
        results.append(scan.get_string("name"))
    scan.close()

    assert results == ["apple", "banana", "orange"]


def test_no_order_by(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), price int)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('apple', 100)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('banana', 50)", tx)

    plan = planner.create_query_plan("SELECT name FROM items", tx)
    scan = plan.open()

    count = 0
    while scan.next():
        count += 1
    scan.close()

    assert count == 2
