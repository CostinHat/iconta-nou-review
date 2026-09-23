---
title: "Cum se declară taxarea inversă în D300"
description: Taxarea inversă apare în D300 pe două rânduri, în funcție de rol — furnizorul declară doar baza, fără TVA (R13), iar beneficiarul autolichidează TVA-ul pe cont propriu, cu efect net zero (R12+R25).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară taxarea inversă în D300

La taxarea inversă, TVA nu circulă între furnizor și beneficiar — furnizorul emite factura fără TVA, iar beneficiarul e cel care calculează și înregistrează TVA-ul, atât ca taxă colectată, cât și ca taxă deductibilă, în același decont. Efectul pentru beneficiar e net zero, dar tranzacția tot trebuie să apară în D300.

## Temeiul legal

::: ghid-temei
**Art. 323 alin. (1) Cod fiscal (Legea 227/2015):** *„... trebuie să depună ... un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă."*

Mecanismul de taxare inversă pentru operațiunile prevăzute la art. 331 Cod fiscal e cel implementat de aplicație (`core/d300.py`, liniile 312-321, 423-433, 435-453) — textul integral al art. 331 nu face parte din citatele verificate ale acestui ghid, dar structura de raportare (rânduri R13/R12/R25) e verificată direct din codul modulului de decont.
:::

## Cum apare taxarea inversă în decont

Din structura confirmată în cod:

- **Pentru furnizor** — livrarea apare pe rândul **R13**, cu baza de impozitare, fără TVA. Furnizorul nu colectează și nu declară TVA pentru această operațiune.
- **Pentru beneficiar** — achiziția apare pe rândurile **R12 (taxă colectată prin autolichidare) + R25 (taxă dedusă)**, cu efect net zero asupra sumei de plată, dar cu obligația de a raporta ambele rânduri, nu doar unul.

Efectul „net zero" nu înseamnă că operațiunea nu se declară — înseamnă că suma de TVA colectată prin autolichidare se anulează cu suma dedusă, în același decont, dar ambele rânduri trebuie completate corect pentru ca decontul să reflecte tranzacția.

## Ce se greșește în practică

- **Se omite complet operațiunea din decont**, pe motiv că „nu e TVA de plată" — chiar cu efect net zero, operațiunea trebuie raportată pe rândurile corespunzătoare (R13 la furnizor, R12+R25 la beneficiar).
- **Beneficiarul completează doar taxa dedusă (R25), fără taxa colectată prin autolichidare (R12)** — taxarea inversă cere ambele înregistrări, nu doar deducerea.
- **Se aplică taxare inversă pe operațiuni care nu se încadrează la art. 331** — regimul e specific anumitor categorii de bunuri/servicii, nu o opțiune generală a părților.

## Ce face iConta.eu

Decontul de TVA v12 (`core/d300.py`) rutează automat operațiunile de taxare inversă pe rândurile corecte — R13 pentru furnizor, R12+R25 pentru beneficiar — pe baza clasificării operațiunii introduse în aplicație. Rândurile manuale pentru taxare inversă, intracomunitar și regularizări se introduc și se editează dintr-un panou dedicat (`core/d300_manual_api.py`), cu buton „Regenerează D300" după fiecare modificare.

[iConta.eu](/)
