# AbraFlexi Closing DE

Web application for preparing documents for closing tax records according to Section 19 of the Tax Code.

## Installation

```bash
pip install flask python-abraflexi
```

## Launch

```bash
python app.py
```

The application will run at: http://localhost:5050

## Functions

- **Connection to AbraFlexi** – enter URL, company, user and password
- (env variables: ABRAFLEXI_URL, ABRAFLEXI_COMPANY, ABRAFLEXI_LOGIN, ABRAFLEXI_PASSWORD)
- **Receivables & Payables** – issued and received invoices with color highlighting after maturity
- **Asset Book** – asset cards, input and residual prices
- **Cash Book** – cash register movements for the selected year
- **Bank statements** – movements on bank accounts
- **Address Book** – suppliers and customers
- **Warehouse inventory** – stock card status
- **Export CSV** – each record can be exported to CSV
- **Checklist** – interactive thesis checklist

## Requirements

- Python 3.8+
- flask
- python-abraflexi
