from conftest import make_fake


def test_i18n_catalogue_returns_keys(client):
    r = client.get("/api/i18n/catalogue")
    d = r.get_json()
    assert "translations" in d
    assert "app.title" in d["translations"]
    assert "yearend.panel_title" in d["translations"]


def test_test_connection_success(client, connection, monkeypatch):
    fake = make_fake(True)
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/test-connection", json=connection)
    d = r.get_json()
    assert d["success"] is True


def test_test_connection_failure(client, connection, monkeypatch):
    fake = make_fake(Exception("Authentication failed"))
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/test-connection", json=connection)
    d = r.get_json()
    assert d["success"] is False


def test_fetch_data_module(client, connection, monkeypatch):
    fake = make_fake([{"kod": "F001", "sumCelkem": "100"}])
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/fetch", json={
        "connection": connection, "module": "adresar", "year": 2025,
    })
    d = r.get_json()
    assert d["success"] is True
    assert d["data"]["contacts"][0]["kod"] == "F001"


def test_export_csv_no_data(client):
    r = client.post("/api/export-csv", json={"rows": []})
    d = r.get_json()
    assert d["success"] is False
