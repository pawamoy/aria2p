def pytest_itemcollected(item):
    item._nodeid = item._nodeid.replace(".py", "").replace("tests/", "").replace("test_", "").replace("_", " ")
