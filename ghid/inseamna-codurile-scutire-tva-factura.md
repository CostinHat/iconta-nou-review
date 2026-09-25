---
title: "Ce înseamnă codurile de scutire TVA din e-Factura?"
description: "De ce o factură cu operațiuni scutite de TVA trebuie să indice temeiul legal al scutirii, și cum se reflectă această obligație în structura facturii electronice RO e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce înseamnă codurile de scutire TVA din e-Factura?

O linie de factură scutită de TVA — export, livrare intracomunitară, prestare medicală, servicii financiare — nu poate rămâne pur și simplu „fără TVA", fără nicio explicație. Legea cere ca factura să arate exact de ce nu s-a aplicat taxa, iar în factura electronică această obligație se traduce printr-un cod de scutire asociat fiecărei operațiuni netaxate.

## Temeiul legal

::: ghid-temei
„(20) Factura cuprinde în mod obligatoriu următoarele informații: [...] l) în cazul în care este aplicabilă o scutire de taxă, trimiterea la dispozițiile aplicabile din prezentul titlu ori din Directiva 112 sau orice altă mențiune din care să rezulte că livrarea de bunuri ori prestarea de servicii face obiectul unei scutiri;"
— Legea nr. 227/2015 (Codul fiscal), art. 319 alin. (20) lit. l) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta, aplicat la factura electronică:

- Orice linie de factură pentru care nu se colectează TVA trebuie să conțină o **mențiune explicită a temeiului scutirii** — fie o trimitere directă la articolul din Codul fiscal (de exemplu art. 294 pentru export, art. 292 pentru scutiri fără drept de deducere), fie o formulare din care să rezulte clar de ce operațiunea nu e taxată.
- În formatul standard al facturii electronice RO e-Factura (bazat pe standardul european de facturare electronică), această mențiune obligatorie se transmite structurat, printr-un cod de motiv al scutirii, atașat fiecărei linii sau categorii de TVA scutite — echivalentul electronic al mențiunii textuale cerute de lege.
- Alegerea codului greșit — de exemplu confundarea unei scutiri fără drept de deducere (art. 292, operațiuni de interes general precum serviciile medicale) cu o scutire cu drept de deducere (art. 294, exporturi și livrări intracomunitare) — nu schimbă doar informația de pe factură, ci și modul în care operațiunea trebuie declarată în decontul de TVA (afectează sau nu dreptul de deducere al furnizorului pentru achizițiile aferente).
- Absența oricărei mențiuni de scutire pe o linie fără TVA face factura neconformă cu cerințele de conținut obligatoriu de la art. 319 alin. (20), indiferent dacă e emisă pe hârtie sau electronic.

## Ce se greșește în practică

- Se emite o factură cu cotă de TVA „0%" sau „scutit", fără nicio trimitere la articolul din Codul fiscal sau la motivul concret al scutirii.
- Se folosește același cod de scutire pentru toate operațiunile netaxate ale firmei, fără să se distingă între scutirile cu drept de deducere (export, livrări IC) și cele fără drept de deducere (activități de interes general).
- Se presupune că un cod de scutire ales greșit în factura electronică e doar o formalitate tehnică, deși el poate schimba tratamentul TVA al operațiunii în raportările ulterioare (D300, D394).

## Ce face iConta.eu

La data acestui ghid, iConta.eu gestionează cotele de TVA aplicabile fiecărei operațiuni prin `core/cote_tva.py` și transmite facturile prin RO e-Factura via `core/efactura_send.py` / `core/efactura_trimitere.py`. Aplicația **nu alege automat codul de motiv al scutirii** pentru fiecare linie de factură fără TVA — utilizatorul trebuie să indice manual temeiul scutirii (articolul din Codul fiscal sau mențiunea echivalentă) la introducerea facturii, iar corectitudinea acestei alegeri, cu efectele ei asupra deducerii TVA, rămâne o responsabilitate a contabilului.

[iConta.eu](/)
