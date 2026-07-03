"""
AbraFlexi Year-End DE
Flask application for tax-evidence year-end closing preparation.
Uses Flask-Babel for i18n (base: English, supported: cs).
"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_babel import Babel, gettext as _, get_locale
import json
import os
import io
import csv
from datetime import datetime, date, timezone

app = Flask(__name__)
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_DEFAULT_TIMEZONE"] = "Europe/Prague"
app.config["LANGUAGES"] = ["en", "cs"]

babel = Babel()


def get_locale_selector():
    lang = request.args.get("lang")
    if lang in app.config["LANGUAGES"]:
        return lang
    lang = request.cookies.get("lang")
    if lang in app.config["LANGUAGES"]:
        return lang
    return request.accept_languages.best_match(app.config["LANGUAGES"]) or "en"


babel.init_app(app, locale_selector=get_locale_selector)


@app.route("/api/i18n/catalogue")
def i18n_catalogue():
    """Return all translation keys for the current locale as JSON."""
    keys = [
        "app.title", "app.subtitle",
        "nav.not_connected", "nav.connecting", "nav.connected", "nav.error",
        "connection.panel_title", "connection.server_url", "connection.company",
        "connection.username", "connection.password", "connection.fiscal_year",
        "connection.test_btn", "connection.success", "connection.no_data",
        "modules.panel_title",
        "modules.overview", "modules.overview_desc",
        "modules.receivables", "modules.receivables_desc",
        "modules.assets", "modules.assets_desc",
        "modules.cash", "modules.cash_desc",
        "modules.bank", "modules.bank_desc",
        "modules.contacts", "modules.contacts_desc",
        "modules.inventory", "modules.inventory_desc",
        "checklist.title",
        "checklist.item1", "checklist.item2", "checklist.item3",
        "checklist.item4", "checklist.item5", "checklist.item6",
        "checklist.item7", "checklist.item8", "checklist.item9",
        "checklist.item10", "checklist.item11", "checklist.item12",
        "checklist.item13", "checklist.item14", "checklist.item15",
        "checklist.item16", "checklist.item17", "checklist.item18",
        "yearend.panel_title",
        "yearend.init_title", "yearend.init_desc",
        "yearend.currencies_btn", "yearend.currency_needed",
        "yearend.opt_preceneni", "yearend.opt_prevod_skladu",
        "yearend.opt_vynechat_nulove", "yearend.opt_zrusit_stare",
        "yearend.opt_dny_bez_pohybu", "yearend.opt_typ_dokl",
        "yearend.opt_ucetni_obdobi",
        "yearend.run_init_btn", "yearend.init_pending",
        "yearend.init_done", "yearend.init_failed", "yearend.init_accepted",
        "yearend.lock_title", "yearend.lock_desc",
        "yearend.lock_zamek_k", "yearend.lock_state_open",
        "yearend.lock_state_half", "yearend.lock_state_locked",
        "yearend.lock_plati_od", "yearend.lock_plati_do",
        "yearend.lock_neucetni", "yearend.lock_modules_title",
        "yearend.lock_select_all", "yearend.lock_select_none",
        "yearend.lock_btn", "yearend.lock_success",
        "yearend.lock_error_no_module",
        "zamek.module.modulFav", "zamek.module.modulFap",
        "zamek.module.modulPhl", "zamek.module.modulZav",
        "zamek.module.modulBan", "zamek.module.modulPok",
        "zamek.module.modulInt", "zamek.module.modulSkl",
        "zamek.module.modulPpp", "zamek.module.modulPpv",
        "zamek.module.modulNap", "zamek.module.modulNav",
        "zamek.module.modulObp", "zamek.module.modulObv",
        "zamek.module.modulMaj", "zamek.module.modulLea",
        "zamek.module.modulMzd",
        "empty.title", "empty.desc", "empty.btn", "empty.no_data",
        "table.export_csv", "table.records",
        "stat.receivables_total", "stat.payables_total",
        "stat.unpaid_receivables", "stat.unpaid_payables",
        "stat.balance", "stat.total_docs", "stat.count",
        "stat.acquisition_cost", "stat.residual_value", "stat.depreciation",
        "stat.movements", "stat.income", "stat.expenses",
        "stat.contacts_count", "stat.stock_cards", "stat.stock_value",
        "col.code", "col.company", "col.var_sym", "col.issue_date",
        "col.due_date", "col.amount", "col.status", "col.name", "col.type",
        "col.acq_date", "col.acq_price", "col.residual", "col.depr_group",
        "col.date", "col.description", "col.doc",
        "col.reg_no", "col.vat_no", "col.email", "col.phone", "col.city",
        "col.qty", "col.buy_price", "col.sell_price", "col.warehouse",
        "status.paid", "status.partial", "status.unpaid",
        "table.issued_invoices", "table.received_invoices",
        "table.asset_register", "table.cash_book",
        "table.bank_statements", "table.address_book", "table.stock_inventory",
        "alert.export_done", "alert.no_export_data", "alert.loading",
        "module.selected", "module.selected_desc",
    ]
    catalogue = {k: _(k) for k in keys}
    resp = jsonify({"locale": str(get_locale()), "translations": catalogue})
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/api/i18n/set-language", methods=["POST"])
def set_language():
    lang = request.json.get("lang", "en")
    if lang not in app.config["LANGUAGES"]:
        return jsonify({"success": False, "message": "Unsupported language"}), 400
    resp = jsonify({"success": True, "lang": lang})
    resp.set_cookie("lang", lang, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return resp


ZAMEK_MODULES = [
    "modulFav", "modulFap", "modulPhl", "modulZav", "modulBan", "modulPok",
    "modulInt", "modulSkl", "modulPpp", "modulPpv", "modulNap", "modulNav",
    "modulObp", "modulObv", "modulMaj", "modulLea", "modulMzd",
]


def build_conn_options(conn, evidence=None, throw=False):
    """Build a python_abraflexi options dict from a connection payload."""
    opts = {
        "url": conn["url"], "company": conn["company"],
        "user": conn["user"], "password": conn["password"],
        "throwException": throw, "ignore404": True,
    }
    if evidence:
        opts["evidence"] = evidence
    return opts


def fetch_evidence(url, company, user, password, evidence, params=None):
    """Fetch all records from an AbraFlexi evidence register."""
    from python_abraflexi import ReadOnly
    ro = ReadOnly(options=build_conn_options(
        {"url": url, "company": company, "user": user, "password": password},
        evidence=evidence,
    ))
    if params:
        ro.default_url_params.update(params)
    result = ro.get_all_from_abraflexi()
    return result if result else []


def serialize_dates(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


@app.route("/")
def index():
    return render_template("index.html", locale=str(get_locale()))


@app.route("/api/test-connection", methods=["POST"])
def test_connection():
    data = request.json
    try:
        from python_abraflexi import ReadOnly
        ro = ReadOnly(options=build_conn_options(data, evidence="adresar", throw=True))
        ro.default_url_params = {"limit": 1}
        ro.get_all_from_abraflexi()
        return jsonify({"success": True, "message": _("connection.success")})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/fetch", methods=["POST"])
def fetch_data():
    data = request.json
    conn = data["connection"]
    module = data["module"]
    year = data.get("year", datetime.now().year - 1)
    date_from = f"{year}-01-01"
    date_to = f"{year}-12-31"

    try:
        result = {}
        if module in ("pohledavky_zavazky", "all"):
            result["issued_invoices"] = fetch_evidence(
                conn["url"], conn["company"], conn["user"], conn["password"],
                "faktura-vydana",
                {"datVyst[gte]": date_from, "datVyst[lte]": date_to,
                 "detail": "custom:kod,nazev,varSym,datVyst,datSplat,sumCelkem,stavUhrK,firma"})
            result["received_invoices"] = fetch_evidence(
                conn["url"], conn["company"], conn["user"], conn["password"],
                "faktura-prijata",
                {"datVyst[gte]": date_from, "datVyst[lte]": date_to,
                 "detail": "custom:kod,nazev,varSym,datVyst,datSplat,sumCelkem,stavUhrK,firma"})
        if module in ("majetek", "all"):
            result["assets"] = fetch_evidence(
                conn["url"], conn["company"], conn["user"], conn["password"],
                "majetek",
                {"detail": "custom:kod,nazev,typMajetkuK,datPoriz,cenaPoriz,zustatkovaCena,odpisGroup,odpisovano"})
        if module in ("pokladna", "all"):
            result["cash"] = fetch_evidence(
                conn["url"], conn["company"], conn["user"], conn["password"],
                "pokladni-pohyb",
                {"datVyst[gte]": date_from, "datVyst[lte]": date_to,
                 "detail": "custom:kod,popis,castka,typPohybuK,datVyst,doklad"})
        if module == "banka":
            result["bank"] = fetch_evidence(
                conn["url"], conn["company"], conn["user"], conn["password"],
                "banka",
                {"datVyst[gte]": date_from, "datVyst[lte]": date_to,
                 "detail": "custom:kod,popis,castka,typPohybuK,datVyst,firma"})
        if module == "adresar":
            result["contacts"] = fetch_evidence(
                conn["url"], conn["company"], conn["user"], conn["password"],
                "adresar",
                {"detail": "custom:kod,nazev,ic,dic,email,tel,mesto"})
        if module == "inventura":
            result["stock"] = fetch_evidence(
                conn["url"], conn["company"], conn["user"], conn["password"],
                "skladova-karta",
                {"detail": "custom:kod,nazev,cenaNakup,cenaProdej,mnozMj,sklad"})

        return jsonify({
            "success": True,
            "data": json.loads(json.dumps(result, default=serialize_dates)),
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/export-csv", methods=["POST"])
def export_csv():
    data = request.json
    rows = data.get("rows", [])
    title = data.get("title", "export")
    if not rows:
        return jsonify({"success": False, "message": _("connection.no_data")})
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys(), extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{title}_{datetime.now().strftime('%Y%m%d')}.csv",
    )


@app.route("/api/yearend/currencies", methods=["POST"])
def yearend_currencies():
    """List currencies and their revaluation rate for a period ('meny-pro-preceneni')."""
    data = request.json
    conn = data["connection"]
    period = data.get("ucetniObdobi")
    try:
        from python_abraflexi import ReadOnly
        ro = ReadOnly(options=build_conn_options(conn, evidence="ucetni-obdobi", throw=True))
        if period:
            ro.default_url_params["ucetniObdobi"] = period
        result = ro.perform_request("meny-pro-preceneni.json")
        currencies = ((result or {}).get("meny") or {}).get("mena") or []
        if isinstance(currencies, dict):
            currencies = [currencies]
        for c in currencies:
            rate = float(c.get("kurz") or 0)
            c["needs_rate"] = rate == 0.0
        return jsonify({"success": True, "currencies": currencies})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/yearend/init", methods=["POST"])
def yearend_init():
    """Trigger 'Inicializace následujícího účetního období' (period init/carry-forward)."""
    data = request.json
    conn = data["connection"]
    try:
        from python_abraflexi import ReadOnly
        ro = ReadOnly(options=build_conn_options(conn, evidence="ucetni-obdobi", throw=True))
        params = {"kontrolaZaokrouhleni": "false"}
        if data.get("ucetniObdobi"):
            params["ucetniObdobi"] = data["ucetniObdobi"]
        for flag in ("preceneni", "prevodSkladu", "vynechatNulove", "zrusitStare"):
            if flag in data:
                params[flag] = "true" if data[flag] else "false"
        if data.get("dnyBezPohybu") not in (None, ""):
            params["dnyBezPohybu"] = int(data["dnyBezPohybu"])
        if data.get("typDokl"):
            params["typDokl"] = data["typDokl"]
        if data.get("preceneni"):
            for code, rate in (data.get("rates") or {}).items():
                params[f"kurz[{code}]"] = rate.get("kurz")
                params[f"kurzMnozstvi[{code}]"] = rate.get("kurzMnozstvi")
        ro.default_url_params.update(params)
        ro.perform_request("inicializace-noveho-obdobi.json")
        return jsonify({
            "success": True,
            "message": _("yearend.init_accepted"),
            "initiated_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/yearend/init-status", methods=["POST"])
def yearend_init_status():
    """Check whether a period initialization has completed (lastUpdate changed)."""
    data = request.json
    conn = data["connection"]
    period = data.get("ucetniObdobi")
    since = data.get("since")
    try:
        from python_abraflexi import ReadOnly
        ro = ReadOnly(options=build_conn_options(conn, evidence="ucetni-obdobi", throw=True))
        ro.default_url_params["detail"] = "custom:kod,lastUpdate"
        records = ro.get_all_from_abraflexi() or []
        record = None
        if period:
            record = next((r for r in records if r.get("kod") == period), None)
        if record is None and records:
            record = records[0]
        last_update = serialize_dates(record["lastUpdate"]) if record and record.get("lastUpdate") else None
        done = bool(last_update and since and last_update > since)
        return jsonify({"success": True, "done": done, "lastUpdate": last_update})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/yearend/lock", methods=["POST"])
def yearend_lock():
    """Lock an accounting period ('zamek' evidence)."""
    data = request.json
    conn = data["connection"]
    modules = data.get("modules") or {}
    if not any(modules.get(m) for m in ZAMEK_MODULES):
        return jsonify({"success": False, "message": _("yearend.lock_error_no_module")})
    try:
        from python_abraflexi import ReadWrite
        rw = ReadWrite(options=build_conn_options(conn, evidence="zamek", throw=True))
        record = {
            "zamekK": data.get("zamekK", "zamek.zamceno"),
            "platiOdData": data["platiOdData"],
            "platiDoData": data["platiDoData"],
            "neucetni": bool(data.get("neucetni", True)),
        }
        for m in ZAMEK_MODULES:
            if modules.get(m):
                record[m] = True
        rw.insert_to_abraflexi(record)
        return jsonify({"success": True, "message": _("yearend.lock_success")})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


if __name__ == "__main__":
    app.run(debug=True, port=5050)
