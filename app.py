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
from datetime import datetime, date

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


def fetch_evidence(url, company, user, password, evidence, params=None):
    """Fetch all records from an AbraFlexi evidence register."""
    from python_abraflexi import ReadOnly
    ro = ReadOnly(options={
        "url": url, "company": company,
        "user": user, "password": password,
        "throwException": False, "ignore404": True,
    })
    ro.set_evidence(evidence)
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
        ro = ReadOnly(options={
            "url": data["url"], "company": data["company"],
            "user": data["user"], "password": data["password"],
            "throwException": True,
        })
        ro.set_evidence("adresar")
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


if __name__ == "__main__":
    app.run(debug=True, port=5050)
