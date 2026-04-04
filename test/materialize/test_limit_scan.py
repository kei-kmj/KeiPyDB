

def test_limit(test_db):
    db, tx = test_db
    planner = db.get_planner()

    planner.execute_update("CREATE TABLE items (name varchar(20), price int)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('apple', 100)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('banana', 50)", tx)
    planner.execute_update("INSERT INTO items (name, price) VALUES ('orange', 80)", tx)

    plan = planner.create_query_plan("SELECT name, price FROM items ORDER BY price LIMIT 2", tx)
    scan = plan.open()

    results = []
    while scan.next():
        results.append(scan.get_int("price"))
    scan.close()

    assert results == [50, 80]