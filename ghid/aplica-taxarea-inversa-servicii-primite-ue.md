---
title: "Când nu se aplică taxarea inversă la servicii primite din UE?"
description: "Taxarea inversă din art. 278 alin. (2) nu se aplică serviciilor livrate prin rețea (gaz, energie electrică) sau facturilor emise de un furnizor cu cod TVA de România, care urmează alte reguli."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când nu se aplică taxarea inversă la servicii primite din UE?

Regula generală e simplă — beneficiarul din România plătește taxa prin taxare inversă la orice serviciu B2B primit de la un furnizor din UE. Există însă două situații confirmate în care nu se aplică exact acest mecanism, deși factura arată identic.

## Temeiul legal

::: ghid-temei
„`tva_taxare_inversa(baza, cota=None)` — TVA prin taxare inversă la AIC/servicii primite; **cota nu are valoare implicită** (obligă apelantul s-o declare explicit...)” — `core/intracomunitar.py`, citat în dosarul F050.

„CF art. 307 alin. (2) — Taxa este datorată de orice persoană impozabilă… care este beneficiar al serviciilor care au locul prestării în România conform art. 278 alin. (2)…” — `cod_fiscal_227_2015_consolidat.txt` L19334-19342.
:::

Regula de bază: la un serviciu B2B primit de la un furnizor stabilit în alt stat membru, cu locul prestării în România conform art. 278 alin. (2), taxa e datorată de beneficiar (art. 307 alin. (2)), prin taxare inversă — formula contabilă 4426=4427 (HG 1/2016, norme la art. 331, pct. 109 alin. 1, aplicabilă „pentru orice alte situații în care se aplică taxarea inversă”).

## Ce se greșește în practică

- **Gazul și energia electrică livrate prin rețea** au aparența unui serviciu IC, dar nu urmează art. 278 alin. (2), ci art. 307 alin. (3) — beneficiarul plătește taxa tot prin taxare inversă, dar temeiul și declararea diferă (D301 tip 4, nu D390). Tratamentul complet e explicat pe larg în ghidul dedicat, „Gazul și energia electrică din UE: de ce nu sunt achiziție intracomunitară”.
- **Furnizorul facturează cu cod de TVA de România**, nu cu un cod străin. Dacă prefixul codului de pe factură e RO, operațiunea nu (mai) e tratată de motorul de operațiuni intracomunitare — furnizorul acționează ca persoană înregistrată în România, iar factura urmează regimul de TVA intern, nu taxarea inversă specifică serviciilor IC.
- Se confundă „fără TVA pe factură” cu „taxare inversă automată” — absența TVA pe factura furnizorului nu suplinește verificarea locului prestării și a calității furnizorului.

## Ce face iConta.eu

Funcția `tva_taxare_inversa` calculează taxa doar dacă i se transmite explicit baza și cota — nu presupune nicio cotă implicită, tocmai ca o schimbare legislativă să nu se rupă tăcut. Ecranul de achiziție intracomunitară din categoria „Extern” cere cod TVA furnizor și tip (bunuri/servicii); pentru operațiunile de tip gaz/energie prin art. 307, sistemul cere temeiul explicit (alin. 3, 5 sau 6) la introducere, tocmai ca să nu se confunde cu un serviciu IC obișnuit.

[iConta.eu](/)
