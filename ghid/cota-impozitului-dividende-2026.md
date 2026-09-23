---
title: "Cota impozitului pe dividende în 2026: cât este"
description: "Cota impozitului reținut la sursă pentru dividendele distribuite din 2026, cu temeiul legal exact și istoricul cotelor anterioare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cota impozitului pe dividende în 2026: cât este

Pentru dividendele distribuite persoanelor fizice începând cu 1 ianuarie 2026, cota impozitului reținut la sursă este **16%**.

## Temeiul legal

::: ghid-temei
"(7) Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final."
— Codul fiscal, art. 97 alin. (7) (`anaf_surse/cod_fiscal_227_2015_consolidat.txt:9470-9474`), modificat de Legea 141/2025 art. II pct. 5, aplicabil dividendelor distribuite începând cu 1 ianuarie 2026 (Legea 141/2025 art. VII lit. c, `anaf_surse/legea_141_2025.txt:653-661`)
:::

Ceea ce contează pentru determinarea cotei aplicabile este **data distribuirii** dividendului (nu data plății și nu 31 decembrie al anului declarației). Istoricul cotelor, pentru context:

| Perioadă | Cotă |
|---|---|
| de la 01.01.2026 | 16% |
| 01.01.2025 – 31.12.2025 | 10% |
| 01.01.2023 – 31.12.2024 | 8% |
| 01.01.2016 – 31.12.2022 | 5% |

## Ce se greșește în practică

Cea mai frecventă eroare apare când un dividend a fost distribuit într-un an, iar plata s-a făcut în anul următor sau eșalonat: se aplică din reflex cota de la data plății, deși legea leagă cota de data distribuirii.

## Ce face iConta.eu

Cota aplicabilă este ținută într-un registru central (`core/common.py`, cheia "impozit_dividend"), sensibil la perioadă, aplicat după data distribuirii. Pentru cazul dividendului distribuit într-un an și plătit eșalonat sau în anul următor, iConta folosește un algoritm dedicat (`core/dividende_curs.py`) care potrivește FIFO fiecare tranșă de plată cu distribuirea corespunzătoare și aplică cota de la data acelei distribuiri, nu o cotă unică la finalul anului — comportament confirmat prin teste dedicate (de exemplu un dividend distribuit în decembrie 2025 la cota 10%, plătit în ianuarie 2026, este impozitat corect la 10%, nu la 16%).

[iConta.eu](/)
