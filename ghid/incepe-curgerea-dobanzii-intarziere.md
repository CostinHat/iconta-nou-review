---
title: "Când începe curgerea dobânzii de întârziere"
description: "Dobânda pentru neplata la termen a obligațiilor fiscale curge din ziua imediat următoare scadenței, nu din ziua constatării restanței."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când începe curgerea dobânzii de întârziere

Momentul de la care curge dobânda de întârziere e fixat de lege la scadență, nu la data la care contribuabilul sau organul fiscal constată efectiv restanța. Diferența contează pentru orice calcul retroactiv al accesoriilor.

## Temeiul legal

::: ghid-temei
„Dobânzile se calculează pentru fiecare zi de întârziere, începând cu ziua imediat următoare termenului de scadență și până la data stingerii sumei datorate, inclusiv."
— Legea 207/2015, art. 174 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Nuanțele care schimbă practic momentul de start, din același articol:

- **Regula generală**: dobânda curge din ziua imediat următoare scadenței (art. 174 alin. 1), până la stingerea integrală a sumei, inclusiv ziua stingerii.
- **Diferențele suplimentare** rezultate din corectarea declarațiilor sau modificarea unei decizii de impunere generează dobândă tot de la scadența inițială a creanței corectate, nu de la data corectării (alin. 2).
- **Nivelul dobânzii** e de 0,02% pentru fiecare zi de întârziere (alin. 5) — o cotă fixă, aplicată indiferent de suma sau tipul obligației.
- **Excepții de moment**: pentru creanțele stinse prin executare silită, dobânda curge până la data procesului-verbal de distribuire (alin. 4 lit. a); pentru debitorii insolvabili fără bunuri urmăribile, până la comunicarea procesului-verbal de insolvabilitate (alin. 4 lit. b).
- **Pentru impozitele cu perioadă fiscală anuală** (impozitul pe venit, de exemplu), regula de start diferă și e detaliată separat, la art. 175 — nu se aplică automat regula lunară de la art. 174.

## Ce se greșește în practică

- Se calculează dobânda de la data la care contabilul descoperă restanța, în loc de la scadența legală (art. 174 alin. 1) — o descoperire târzie nu amână momentul de start al dobânzii, doar întârzie constatarea ei.
- Se aplică regula generală (art. 174) și pentru impozitele cu perioadă fiscală anuală, unde momentul de start e stabilit separat, la art. 175, cu reguli proprii pentru plățile anticipate și regularizarea anuală.
- Se presupune că o corectare ulterioară a declarației „resetează" curgerea dobânzii de la data corectării — alin. (2) prevede explicit că dobânda se datorează de la scadența inițială a diferenței stabilite.

## Ce face iConta.eu

iConta.eu urmărește termenele de depunere a declarațiilor (scadențarul din `core/scadente.py`) și semnalează declarațiile nedepuse la termen prin semaforul de conformare fiscală (`core/control_fiscal_api.py`). Nu am identificat însă în cod un calculator al dobânzii de întârziere propriu-zise (0,02%/zi, conform art. 174) pentru sumele neplătite — calculul accesoriilor fiscale rămâne, la această dată, o operațiune făcută direct de organul fiscal, pe fișa pe plătitor, nu în aplicație.

[iConta.eu](/)
