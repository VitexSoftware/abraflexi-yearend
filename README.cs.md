# AbraFlexi Závěrka DE

Webová aplikace pro přípravu podkladů k uzavření daňové evidence dle § 19 ZoÚ.

## Instalace

```bash
pip install flask python-abraflexi
```

## Spuštění

```bash
python app.py
```

Aplikace poběží na: http://localhost:5050

## Funkce

- **Připojení k AbraFlexi** – zadejte URL, firmu, uživatele a heslo
  - (env proměnné: ABRAFLEXI_URL, ABRAFLEXI_COMPANY, ABRAFLEXI_LOGIN, ABRAFLEXI_PASSWORD)
- **Pohledávky & Závazky** – vydané a přijaté faktury s barevným zvýrazněním po splatnosti
- **Kniha majetku** – karty majetku, vstupní a zůstatkové ceny
- **Pokladní kniha** – pohyby v pokladně za vybraný rok
- **Bankovní výpisy** – pohyby na bankovních účtech
- **Adresář** – dodavatelé a odběratelé
- **Inventura skladu** – stav skladových karet
- **Export CSV** – každá evidence lze exportovat do CSV
- **Kontrolní seznam** – interaktivní checklist závěrkových prací

## Požadavky

- Python 3.8+
- flask
- python-abraflexi
