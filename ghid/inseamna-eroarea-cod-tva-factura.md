---
title: "Ce înseamnă eroarea de cod TVA în e-Factura?"
description: "De ce apare eroarea de cod de TVA la trimiterea unei facturi în RO e-Factura și cum se deosebește codul de înregistrare în scopuri de TVA de codul de identificare fiscală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce înseamnă eroarea de cod TVA în e-Factura?

Codul fiscal cere ca pe factură să apară, după caz, **fie** codul de înregistrare în scopuri de TVA (CUI cu prefixul „RO", pentru plătitorii de TVA), **fie** codul de identificare fiscală simplu (CUI fără prefix, pentru neplătitorii de TVA). O factură XML trimisă în RO e-Factura cu prefixul greșit — „RO" atașat la CUI-ul unei firme neplătitoare de TVA, sau lipsă la o firmă plătitoare — nu se potrivește cu statusul real al firmei din Registrul contribuabililor și declanșează eroarea de cod TVA la validare.

## Temeiul legal

::: ghid-temei
„(20) [...] d) denumirea/numele, adresa și codul de înregistrare în scopuri de TVA sau, după caz, codul de identificare fiscală ale persoanei impozabile care a livrat bunurile sau a prestat serviciile; [...] f) denumirea/numele și adresa beneficiarului bunurilor sau serviciilor, precum și codul de înregistrare în scopuri de TVA sau codul de identificare fiscală al beneficiarului, dacă acesta este o persoană impozabilă ori o persoană juridică neimpozabilă."
— Legea nr. 227/2015 privind Codul fiscal, art. 319 alin. (20) lit. d) și f) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Legea distinge clar între cele două tipuri de cod care pot apărea pe o factură:

- **Codul de înregistrare în scopuri de TVA** (conform art. 316) — se folosește numai de persoanele impozabile înregistrate ca plătitoare de TVA, și se scrie cu prefixul „RO" înaintea cifrelor CUI.
- **Codul de identificare fiscală** — CUI-ul simplu, fără prefix „RO", pentru persoanele care nu sunt plătitoare de TVA (de exemplu firme la regim de scutire, sub plafon).

Amestecarea celor două — atribuirea prefixului „RO" unei firme neplătitoare, sau lipsa lui pentru o firmă plătitoare — face ca identificatorul din factura electronică să nu corespundă cu statusul de TVA înregistrat la ANAF pentru acel CUI, ceea ce provoacă eroarea de validare semnalată la trimiterea prin RO e-Factura.

## Ce se greșește în practică

- Se aplică automat prefixul „RO" la codul fiscal al oricărui partener, indiferent dacă e sau nu plătitor de TVA — corect e prefixul doar pentru cei înregistrați conform art. 316.
- Se ignoră modificările de status TVA ale unui partener (de exemplu, o firmă care a trecut de la neplătitor la plătitor de TVA, sau invers, prin anulare de cod) — dacă datele partenerului nu sunt actualizate, factura poate purta codul vechi, incompatibil cu statusul curent.
- Se introduce manual codul de TVA al beneficiarului cu spații, cratime sau litere mici, în loc de formatul strict „RO" + cifre — chiar dacă CUI-ul e corect, formatarea greșită produce aceeași eroare de validare.

## Ce face iConta.eu

iConta.eu construiește codul de TVA pentru factura electronică din CUI-ul înregistrat, prin funcția `_vatid()` din `core/efactura_send.py`. Pentru **furnizor** (firma proprie, emitentul facturii), codul din cod confirmă exact regula de mai sus: prefixul „RO" se adaugă în fața cifrelor CUI **numai** atunci când firma e marcată drept plătitoare de TVA (`sup_vat = _vatid(furnizor.get("cui")) if furnizor.get("platitor_tva") else ""`) — respectând distincția din art. 319 alin. (20) din Codul fiscal între codul de înregistrare în scopuri de TVA și codul de identificare fiscală simplu. Pentru **client/beneficiar**, verificarea directă în cod arată însă că regula NU e aplicată condiționat: `cli_vat = _vatid(client.get("cui"))` adaugă prefixul „RO" necondiționat, indiferent dacă partenerul e sau nu marcat plătitor de TVA — o inconsecvență reală față de distincția din lege, pe latura de beneficiar. Ce nu automatizează astăzi aplicația, pe niciuna dintre laturi: verificarea în timp real a statusului de plătitor de TVA al unui partener direct din Registrul contribuabililor ANAF, înainte de emiterea facturii — corectitudinea datelor introduse pentru un partener rămâne responsabilitatea contabilului care completează fișa partenerului.

[iConta.eu](/)
