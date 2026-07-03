from conftest import make_fake


def test_lock_no_module_selected_rejected_without_contacting_abraflexi(client, connection, monkeypatch):
    fake = make_fake(True)
    monkeypatch.setattr("python_abraflexi.ReadWrite", fake)

    r = client.post("/api/yearend/lock", json={
        "connection": connection,
        "zamekK": "zamek.zamceno",
        "platiOdData": "2026-01-01",
        "platiDoData": "2026-12-31",
        "modules": {},
    })
    d = r.get_json()

    assert d["success"] is False
    assert fake.instances == []


def test_lock_success(client, connection, monkeypatch):
    fake = make_fake(True)
    monkeypatch.setattr("python_abraflexi.ReadWrite", fake)

    r = client.post("/api/yearend/lock", json={
        "connection": connection,
        "zamekK": "zamek.zamceno",
        "platiOdData": "2026-01-01",
        "platiDoData": "2026-12-31",
        "neucetni": True,
        "modules": {"modulFap": True},
    })
    d = r.get_json()

    assert d["success"] is True
    instance = fake.instances[0]
    call = instance.calls[0]
    assert call[0] == "insert_to_abraflexi"
    record = call[1]
    assert record["modulFap"] is True
    assert "modulFav" not in record


def test_lock_abraflexi_rejection_surfaced(client, connection, monkeypatch):
    fake = make_fake(Exception("HTTP 403: User is not authorized"))
    monkeypatch.setattr("python_abraflexi.ReadWrite", fake)

    r = client.post("/api/yearend/lock", json={
        "connection": connection,
        "zamekK": "zamek.zamceno",
        "platiOdData": "2026-01-01",
        "platiDoData": "2026-12-31",
        "modules": {"modulBan": True},
    })
    d = r.get_json()

    assert d["success"] is False
    assert "not authorized" in d["message"]
