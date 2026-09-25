---
title: "Cum se declară vânzările prin curier internațional"
description: "Regimul de TVA pentru vânzarea la distanță de bunuri expediate către clienți din alte state, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară vânzările prin curier internațional

O vânzare expediată prin curier către un client dintr-un alt stat nu e o livrare oarecare — Codul fiscal o definește explicit ca „vânzare la distanță", cu reguli proprii de TVA, diferite de o livrare internă.

## Temeiul legal

::: ghid-temei
„Vânzare la distanță de bunuri importate din teritorii terțe sau țări terțe înseamnă o livrare de bunuri expediate sau transportate de furnizor sau în numele acestuia, inclusiv în cazul în care furnizorul intervine în mod indirect în transportul sau expedierea bunurilor, dintr-un teritoriu terț sau dintr-o țară terță către un client dintr-un stat membru, dacă sunt îndeplinite [...] condițiile [prevăzute la lit. a) și b)]."

„Prin excepție de la prevederile alin. (1) lit. a), locul livrării în cazul vânzărilor la distanță de bunuri importate din teritorii terțe sau țări terțe într-un alt stat membru decât cel în care se încheie expedierea sau transportul bunurilor către client este considerat a fi locul unde se află bunurile în momentul în care se încheie expedierea sau transportul acestora către client."
— Codul fiscal, art. 266 alin. (1) pct. 36 și art. 275 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Distincția esențială pentru o firmă care vinde prin curier internațional:

- Dacă bunurile pleacă **dintr-un stat membru UE** către un client dintr-un alt stat membru, operațiunea e o **vânzare la distanță intracomunitară** — locul livrării (și deci statul unde se datorează TVA) depinde de plafonul de vânzări la distanță și de opțiunile exercitate, regim gestionat de regulă prin sistemul OSS (ghișeul unic).
- Dacă bunurile pleacă **dintr-un teritoriu/țară terță** (în afara UE) direct către clientul final, se aplică definiția specifică de „vânzare la distanță de bunuri importate din teritorii terțe" — cu obligații declarative proprii (inclusiv posibil prin IOSS, pentru transporturi de valoare mică).
- Curierul e doar mijlocul de transport — regimul de TVA nu depinde de faptul că livrarea se face „prin curier", ci de traseul real al bunurilor (de unde pleacă, unde ajunge) și de statutul fiscal al cumpărătorului (persoană impozabilă sau consumator final).

## Ce se greșește în practică

- Se tratează orice livrare externă „prin curier" ca pe o export simplă, fără verificarea condițiilor de la art. 266 alin. (1) pct. 36 și art. 275 alin. (3) — regimul de vânzare la distanță are propriile praguri și obligații, distincte de exportul clasic.
- Se ignoră plafonul de vânzări la distanță intracomunitare, presupunând că TVA se datorează mereu doar în statul de plecare a mărfii — peste plafon, locul livrării (și obligația de TVA) se mută în statul de destinație.
- Se confundă vânzarea la distanță cu o simplă expediere de mostre sau documente fără valoare comercială — regimul descris se aplică livrărilor de bunuri cu titlu oneros, către clienți finali, nu oricărui colet trimis prin curier.

## Ce face iConta.eu

Facturile de vânzare către clienți externi se emit prin fluxul general de facturare. iConta.eu are un modul dedicat pentru declarația D398 (regimurile speciale OSS/IOSS, `core/d398.py`), care generează XML-ul de declarație, dar sumele pe fiecare stat de consum se introduc manual, nu se deduc automat din facturile emise — încadrarea corectă în regimul de vânzare la distanță (plafoane, stat de destinație) rămâne o verificare manuală a contabilului.

[iConta.eu](/)
