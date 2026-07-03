# AbraFlexi Závěrka DE

Webová aplikace pro přípravu podkladů k uzavření daňové evidence dle § 19 ZoÚ.

## Instalace

```bash
pip install -r requirements.txt
# nebo: pip install flask "python-abraflexi>=1.1.2" flask-babel
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
- **Kontrolní seznam** – interaktivní 18-bodový checklist závěrkových prací
  (body 13 a 15 jsou napojeny na skutečné akce konce roku níže, zbytek jsou
  ruční kroky vyžadující úsudek – inventury, rezervy, časové rozlišení)

## Akce konce roku

Na rozdíl od výše uvedených čistě čtecích přehledů provádí tyto akce
skutečné zápisy do AbraFlexi a vyžadují uživatele s odpovídajícím
oprávněním k zápisu:

- **Inicializace účetního období** – převede konečné zůstatky do
  následujícího účetního období. Lze spouštět opakovaně. Volitelně provede
  přecenění neuhrazených dokladů v cizí měně (nejprve načtěte aktuální kurzy
  tlačítkem „Zkontrolovat měny pro přecenění“; měna s chybějícím/nulovým
  kurzem musí mít kurz zadaný ručně) a převod skladu. AbraFlexi zpracovává
  inicializaci na pozadí (HTTP 202 Accepted) – aplikace průběžně kontroluje
  dokončení, u větších dat to může chvíli trvat.
- **Uzamknutí účetního období** – uzamkne období pro jeden nebo více modulů
  dokladů (vydané/přijaté faktury, banka, pokladna, majetek atd.), takže
  doklady již nelze upravovat. Je nutné vybrat alespoň jeden modul.

## Požadavky

- Python 3.8+
- flask
- flask-babel
- python-abraflexi >= 1.1.2
