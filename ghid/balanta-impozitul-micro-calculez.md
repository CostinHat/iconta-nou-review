---
title: "Balanta și impozitul micro: cum îl calculez"
description: Impozitul micro se calculează trimestrial, la cota de 1%, aplicată veniturilor din balanță — soldul creditor al conturilor de venituri din exploatare (70x) și financiare (75x, 76x), din care se scade debitul contului 709 (reduceri comerciale acordate).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Balanta și impozitul micro: cum îl calculez

Impozitul pe veniturile microîntreprinderilor se calculează direct din balanța de verificare a trimestrului — nu dintr-un profit contabil, ca la impozitul pe profit. Baza de calcul e veniturile realizate, cu câteva excluderi prevăzute explicit de lege.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe veniturile microîntreprinderilor este de 1%." — Codul fiscal, art. 51 alin. (1), astfel cum a fost modificat de OUG 89/2025, de la 1 ianuarie 2026. Baza impozabilă o reprezintă „veniturile din orice sursă", din care se scad categoriile enumerate la art. 53 alin. (1) lit. a)-o).
:::

## Cum se citește baza din balanță

Veniturile care intră în baza impozabilă se preiau din soldul creditor al conturilor din clasele:

- **70x** — venituri din vânzarea de produse, mărfuri, servicii;
- **75x** — venituri din exploatare (altele decât cele din vânzări);
- **76x** — venituri financiare.

Din suma acestor solduri creditoare se scade **debitul contului 709** (reduceri comerciale acordate), care diminuează veniturile din vânzări. Formula rezultată: impozitul = (venituri 70x + 75x + 76x − 709) × 1%.

Din baza impozabilă se exclud, potrivit art. 53 alin. (1), categoriile enumerate explicit de lege — de exemplu, veniturile din diferențe de curs valutar (lit. h) și veniturile financiare din creanțe/datorii cu decontare în funcție de cursul unei valute (lit. i), printre altele.

## Ce se greșește în practică

- Se pornește calculul de la profitul contabil (venituri minus cheltuieli), ca la impozitul pe profit — impozitul micro se calculează direct pe venituri, fără a scădea cheltuielile.
- Se omite scăderea contului 709 din baza de calcul, umflând artificial veniturile impozabile atunci când există reduceri comerciale acordate clienților.
- Se include în bază, fără verificare, întreaga clasă 76x, deși unele venituri financiare din ea (diferențele de curs valutar, de exemplu) sunt excluse explicit de lege la art. 53 alin. (1).

## Ce face iConta.eu

Motorul de calcul (`core/d100.py`) preia baza impozabilă din soldurile conturilor 70x + 75x + 76x, minus debitul contului 709, și aplică cota de 1% (cu rotunjire aritmetică, nu bancară), pentru fiecare trimestru calendaristic. De reținut: verificat direct în cod, funcția care preia baza include întreaga clasă 76x, fără o excludere explicită a conturilor 765 (diferențe de curs) sau 766 — dacă firma are venituri financiare din diferențe de curs valutar semnificative, verificați manual dacă acestea au fost corect excluse din baza impozabilă declarată, până la o clarificare suplimentară a acestui punct.

[iConta.eu](/)
