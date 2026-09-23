---
title: Cum raportez în D394 operațiunile din sistemul TVA la încasare
description: TVA la încasare schimbă doar momentul de exigibilitate al taxei (art. 282 CF) — operațiunea rămâne aceeași factură, cu aceleași părți și sume; tratamentul specific al acestor operațiuni în formularul D394 nu a fost verificat în cercetarea de temei a acestui ghid.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum raportez în D394 operațiunile din sistemul TVA la încasare

Acest ghid tratează separat ce e sigur — mecanismul legal care stă la baza TVA la încasare — de ce nu am putut confirma din cercetarea disponibilă: comportamentul exact al declarației D394 pentru aceste operațiuni.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3) din Codul fiscal (Legea 227/2015)**: *„Prin excepție de la prevederile alin. (1) și alin. (2) lit. a), exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens..."*
:::

## Ce e sigur

TVA la încasare (art. 282 alin. (3)) modifică exclusiv **momentul** la care taxa devine exigibilă — nu modifică factura în sine, valoarea operațiunii, părțile implicate sau natura ei. Aceeași concluzie e confirmată direct în codul aplicației, la nivelul decontului de TVA (D300): sumele calculate pentru firmele cu TVA la încasare ajung tot în rândurile obișnuite de TVA colectată (R9_1/R9_2, R10, R11) — **nu există un rând separat „TVA la încasare"** în D300. Regimul de exigibilitate schimbă doar perioada în care suma apare în decont, nu structura raportării.

## Ce nu am putut confirma

Cercetarea de temei pentru acest ghid a acoperit modulele `core/tva_incasare.py`, `core/cota_tva_incasare.py`, `core/d300.py`, `core/avansuri.py` și ecranele de facturare/operațiuni speciale — **nu a inclus o citire a modulului de generare D394** (`core/d394.py` nu a fost consultat). Nu putem confirma din acest dosar:

- dacă aplicația marchează distinct, în fișierul D394, operațiunile efectuate de o firmă înscrisă la TVA la încasare;
- dacă valoarea/perioada raportată în D394 urmează data facturii sau data încasării;
- dacă există vreun indicator specific „TVA la încasare" în structura formularului, așa cum e generat de aplicație.

Conform regulii dosarului de cercetare — nicio afirmație fără sursă verificată — nu vom prezenta niciunul din aceste puncte ca fiind confirmat.

## Ce se greșește în practică

- **Se presupune, fără verificare, că D394 urmează automat regimul de exigibilitate din D300.** Cele două declarații pot avea reguli de raportare diferite, iar acest dosar nu confirmă comportamentul aplicației pe D394.
- **Se amână raportarea în D394 până la încasare**, prin analogie greșită cu mecanismul TVA la încasare din D300, fără o verificare directă a regulilor proprii declarației 394.

## Ce face iConta.eu

La data acestui ghid, cercetarea de temei nu a acoperit modulul D394 — nu putem confirma dacă și cum aplicația tratează distinct operațiunile supuse TVA la încasare în această declarație. Recomandăm verificarea directă a modulului tehnic sau consultarea echipei de suport înainte de a considera un comportament ca fiind automatizat.

[iConta.eu](/)
