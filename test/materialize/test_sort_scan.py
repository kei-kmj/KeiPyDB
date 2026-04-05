import pytest


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


def test_sort_scan_desc(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), price int)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('apple', 100)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('banana', 50)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('orange', 80)", tx)

    plan = planner.create_query_plan("SELECT name, price FROM items ORDER BY price DESC", tx)
    scan = plan.open()

    results = []
    while scan.next():
        results.append(scan.get_int("price"))
    scan.close()

    assert results == [100, 80, 50]


def test_vector_sort_scan(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), embedding vector(3))", tx)
    planner.execute_update("INSERT INTO items (name, embedding) VALUES ('far', '[0.0, 0.0, 1.0]')", tx)
    planner.execute_update("INSERT INTO items (name, embedding) VALUES ('close', '[1.0, 0.0, 0.0]')", tx)
    planner.execute_update("INSERT INTO items (name, embedding) VALUES ('middle', '[0.7, 0.7, 0.0]')", tx)

    plan = planner.create_query_plan("SELECT name FROM items ORDER BY embedding <-> '[1.0, 0.0, 0.0]' LIMIT 3", tx)
    scan = plan.open()

    results = []
    while scan.next():
        results.append(scan.get_string("name"))
    scan.close()

    assert results == ["close", "middle", "far"]


def test_sort_scan_before_first(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), price int)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('apple', 100)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('banana', 50)", tx)

    plan = planner.create_query_plan("SELECT name, price FROM items ORDER BY price", tx)
    scan = plan.open()

    # 1回目のスキャン
    first_scan_results = []
    while scan.next():
        first_scan_results.append(scan.get_int("price"))

    # before_firstでリセットして2回目のスキャン
    scan.before_first()
    second_scan_results = []
    while scan.next():
        second_scan_results.append(scan.get_int("price"))

    scan.close()

    assert first_scan_results == [50, 100]
    assert second_scan_results == [50, 100]


def test_sort_scan_get_methods(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), price int, embedding vector(3))", tx)
    planner.execute_update("INSERT INTO items (name, price, embedding) VALUES ('apple', 100, '[1.0, 0.0, 0.0]')", tx)
    planner.execute_update("INSERT INTO items (name, price, embedding) VALUES ('banana', 50, '[0.0, 1.0, 0.0]')", tx)

    plan = planner.create_query_plan("SELECT name, price, embedding FROM items ORDER BY price", tx)
    scan = plan.open()
    scan.next()

    assert scan.get_int("price") == 50
    assert scan.get_string("name") == "banana"
    assert scan.get_vector("embedding") == pytest.approx([0.0, 1.0, 0.0])
    assert scan.has_field("price") is True
    assert scan.has_field("nonexistent") is False

    scan.close()


def test_sort_scan_runtime_error(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), price int)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('apple', 100)", tx)

    plan = planner.create_query_plan("SELECT name, price FROM items ORDER BY price", tx)
    scan = plan.open()

    # next()を呼ぶ前はcurrent_scanがNone
    with pytest.raises(RuntimeError):
        scan.get_int("price")

    scan.close()


def test_sort_scan_save_and_restore_position(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), price int)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('apple', 100)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('banana', 50)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('orange', 80)", tx)

    plan = planner.create_query_plan("SELECT name, price FROM items ORDER BY price", tx)
    scan = plan.open()

    scan.next()  # banana(50)
    scan.next()  # orange(80)
    scan.save_position()

    scan.next()  # apple(100)
    assert scan.get_int("price") == 100

    scan.restore_position()
    assert scan.get_int("price") == 80

    scan.close()
