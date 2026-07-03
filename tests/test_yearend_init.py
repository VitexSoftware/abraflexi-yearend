from conftest import make_fake


def test_currencies_happy_path(client, connection, monkeypatch):
    fake = make_fake({"meny": {"mena": [
        {"kod": "EUR", "kurz": "24.725", "kurzMnozstvi": "1.0"},
        {"kod": "USD", "kurz": "0.0", "kurzMnozstvi": "1.0"},
    ]}})
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/yearend/currencies", json={"connection": connection})
    d = r.get_json()

    assert d["success"] is True
    assert d["currencies"][0]["kod"] == "EUR"
    assert d["currencies"][0]["needs_rate"] is False
    assert d["currencies"][1]["kod"] == "USD"
    assert d["currencies"][1]["needs_rate"] is True


def test_init_trigger_success(client, connection, monkeypatch):
    fake = make_fake(True)
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/yearend/init", json={
        "connection": connection, "ucetniObdobi": "2025",
        "preceneni": False, "prevodSkladu": True,
    })
    d = r.get_json()

    assert d["success"] is True
    assert "initiated_at" in d
    instance = fake.instances[0]
    assert instance.calls[0][0] == "perform_request"
    assert instance.calls[0][1] == "inicializace-noveho-obdobi.json"


def test_init_trigger_passes_double_entry_account_params(client, connection, monkeypatch):
    fake = make_fake(True)
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/yearend/init", json={
        "connection": connection,
        "ucetOtv": "701000", "ucetZav": "702000",
        "ucetPre": "710000", "ucetVys": "431000",
    })
    d = r.get_json()

    assert d["success"] is True
    instance = fake.instances[0]
    assert instance.default_url_params["ucetOtv"] == "701000"
    assert instance.default_url_params["ucetZav"] == "702000"
    assert instance.default_url_params["ucetPre"] == "710000"
    assert instance.default_url_params["ucetVys"] == "431000"


def test_init_trigger_omits_account_params_when_blank(client, connection, monkeypatch):
    fake = make_fake(True)
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/yearend/init", json={"connection": connection})
    d = r.get_json()

    assert d["success"] is True
    instance = fake.instances[0]
    assert "ucetOtv" not in instance.default_url_params


def test_init_trigger_missing_currency_rate_surfaces_error(client, connection, monkeypatch):
    fake = make_fake(Exception("HTTP 400: chybí kurz pro měnu EUR"))
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/yearend/init", json={
        "connection": connection, "preceneni": True, "rates": {},
    })
    d = r.get_json()

    assert d["success"] is False
    assert "kurz" in d["message"]


def test_init_status_not_done(client, connection, monkeypatch):
    fake = make_fake([{"kod": "2025", "lastUpdate": "2026-01-01T00:00:00"}])
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/yearend/init-status", json={
        "connection": connection, "ucetniObdobi": "2025",
        "since": "2027-01-01T00:00:00",
    })
    d = r.get_json()

    assert d["success"] is True
    assert d["done"] is False


def test_init_status_done(client, connection, monkeypatch):
    fake = make_fake([{"kod": "2025", "lastUpdate": "2027-01-01T00:00:00"}])
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/yearend/init-status", json={
        "connection": connection, "ucetniObdobi": "2025",
        "since": "2026-01-01T00:00:00",
    })
    d = r.get_json()

    assert d["success"] is True
    assert d["done"] is True


def test_init_status_without_period_code_checks_all_periods(client, connection, monkeypatch):
    # Regression test: when no ucetniObdobi is given (the common case - it
    # defaults to AbraFlexi's own "current" period), the endpoint must not
    # just look at an arbitrary single record. AbraFlexi may report several
    # period records and the one that actually got updated isn't
    # necessarily the first one returned.
    fake = make_fake([
        {"kod": "2024", "lastUpdate": "2024-11-20T00:00:00"},
        {"kod": "2025", "lastUpdate": "2026-01-01T00:00:00"},
        {"kod": "2026", "lastUpdate": "2027-06-01T00:00:00"},
    ])
    monkeypatch.setattr("python_abraflexi.ReadOnly", fake)

    r = client.post("/api/yearend/init-status", json={
        "connection": connection, "since": "2027-01-01T00:00:00",
    })
    d = r.get_json()

    assert d["success"] is True
    assert d["done"] is True
    assert d["lastUpdate"] == "2027-06-01T00:00:00"
