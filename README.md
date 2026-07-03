# AbraFlexi Closing DE

Web application for preparing documents for closing tax records according to Section 19 of the Tax Code.

## Installation

### From Debian Package

The easiest way to install the application is via the Debian package:

```bash
sudo dpkg -i abraflexi-yearend_0.1.0_all.deb
sudo apt-get install -f
```

### From Source

```bash
pip install -r requirements.txt
# or: pip install flask "python-abraflexi>=1.1.2" flask-babel
```

## Launch

### Manual Launch

```bash
abraflexi-yearend
```

The application will run at: http://localhost:5050

## Web Server Configuration

To run the application in a production environment, it is recommended to use a web server like Apache or Nginx as a reverse proxy.

### Apache Configuration

1. Install required modules:
   ```bash
   sudo a2enmod proxy proxy_http
   ```

2. Create a new configuration file `/etc/apache2/sites-available/abraflexi-yearend.conf`:
   ```apache
   <VirtualHost *:80>
       ServerName abraflexi-yearend.example.com

       ProxyPreserveHost On
       ProxyPass / http://127.0.0.1:5050/
       ProxyPassReverse / http://127.0.0.1:5050/

       ErrorLog ${APACHE_LOG_DIR}/abraflexi-yearend-error.log
       CustomLog ${APACHE_LOG_DIR}/abraflexi-yearend-access.log combined
   </VirtualHost>
   ```

3. Enable the site and restart Apache:
   ```bash
   sudo a2ensite abraflexi-yearend.conf
   sudo systemctl restart apache2
   ```

### Nginx Configuration

1. Create a new configuration file `/etc/nginx/sites-available/abraflexi-yearend`:
   ```nginx
   server {
       listen 80;
       server_name abraflexi-yearend.example.com;

       location / {
           proxy_pass http://127.0.0.1:5050;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

2. Enable the site and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/abraflexi-yearend /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

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
- **Checklist** – interactive 18-step year-end checklist (items 13 and 15 are
  wired to the real Year-End Actions below; the rest are manual/judgment
  steps such as inventory counts, provisions and accruals)

## Year-End Closing Actions

Unlike the read-only dashboards above, these perform real write operations
against AbraFlexi and require an AbraFlexi user with appropriate write
permissions:

- **Period Initialization** ("Inicializace následujícího účetního období") –
  carries forward closing balances into the next accounting period. Can be
  run repeatedly. Optionally revalues unpaid foreign-currency documents
  (fetch current rates first via "Check currencies for revaluation"; any
  currency with a missing/zero rate must have one entered manually) and
  carries forward the warehouse. AbraFlexi processes this asynchronously
  (HTTP 202 Accepted, background job) — the UI polls for completion and can
  take a while on large datasets.
- **Period Lock** ("Uzamknutí účetního období") – locks the accounting period
  for one or more document modules (issued/received invoices, bank, cash,
  assets, etc.) so documents can no longer be modified. At least one module
  must be selected.

## Requirements

- Python 3.8+
- flask
- flask-babel
- python-abraflexi >= 1.1.2
