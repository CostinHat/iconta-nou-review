---
title: "D101 precompletată: cum o verific 2026"
description: Checklist de verificare a D101 pregătită automat de aplicație pentru 2026 — inclusiv o atenționare importantă privind cota IMCA calculată de motor.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D101 precompletată: cum o verific 2026

D101 precompletată automat din balanță economisește timp, dar nu înlocuiește verificarea contabilului. Pentru 2026, există cel puțin o zonă în care valoarea generată de aplicație trebuie corectată manual înainte de depunere.

## Temeiul legal

::: ghid-temei
Art.18^1 alin.(16) CF (introdus de OUG nr.89/2025, MO 1203/24.12.2025, în vigoare de la 01.01.2026): „Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin.(3) este 0,5%."

„D101 nu se poate genera fără CUI valid (checksum verificat prin `core.identitate.valideaza_cui`), denumire, adresă, cod CAEN pe 4 cifre; plus erorile de declarant din `core.firma_profil_api.erori_declarant`."
— sursă: `core/d101.py`, funcția `erori_generare`, liniile 366–388, dosar de cercetare F027.
:::

Cota corectă de IMCA (impozitul minim pe cifra de afaceri) pentru anul fiscal 2026 este **0,5%** din baza de calcul (VT − Vs − I − A), nu 1% — modificare introdusă de OUG 89/2025, în vigoare de la 1 ianuarie 2026, valabilă pentru acest an fiscal.

## Ce se greșește în practică

La firmele eligibile pentru IMCA (cifră de afaceri de peste 50.000.000 EUR în anul precedent), verificarea insuficientă a cotei aplicate poate dubla efectiv impozitul minim calculat — diferența dintre 1% și 0,5% aplicată la o bază mare de calcul înseamnă sume semnificative. O a doua greșeală obișnuită este ignorarea faptului că D101 e strict declarația anuală de definitivare — plățile anticipate trimestriale (cod obligație 103) se verifică separat, prin D100.

## Ce face iConta.eu

Iată ce trebuie verificat punct cu punct la o D101 precompletată de aplicație pentru 2026:

- **CUI, denumire, adresă, cod CAEN (4 cifre)** — declarația nu se generează fără acestea, deci prezența lor e deja validată automat.
- **Contul 691** — dacă are sold debitor pozitiv, iar rândul de cheltuieli nedeductibile (P23) e 0, aplicația emite un avertisment; nu-l ignorați, e un semn de posibilă subevaluare a impozitului.
- **Rezerva legală (P13)** — calculată automat din profitul contabil brut plus cheltuiala cu impozitul, plafonată corect; verificați dacă valoarea calculată corespunde realității, mai ales dacă ați introdus manual o valoare diferită.
- **IMCA, dacă firma e eligibilă** — **atenție**: la data acestui ghid, motorul de calcul din aplicație aplică o cotă de 1% în formula IMCA, deși legea prevede explicit 0,5% pentru anul fiscal 2026. Dacă firma dumneavoastră depășește pragul de 50.000.000 EUR cifră de afaceri, verificați manual acest calcul și corectați cota la 0,5% înainte de depunere — nu vă bazați pe valoarea generată automat pentru acest rând, până la actualizarea motorului de calcul.
- **Rectificativă** — dacă aveți nevoie să corectați o D101 deja depusă, rețineți că generarea unei D101 rectificative nu este încă disponibilă din interfața aplicației; corecția se face în prezent direct la ANAF.

[iConta.eu](/)
