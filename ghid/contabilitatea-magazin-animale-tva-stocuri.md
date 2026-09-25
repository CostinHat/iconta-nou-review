---
title: "Contabilitatea unui magazin de animale: TVA și stocuri"
description: "Cotele diferite de TVA aplicabile într-un magazin de animale — hrană și animale vii la cotă redusă, accesorii la cotă standard — conform art. 291 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Contabilitatea unui magazin de animale: TVA și stocuri

Un magazin de animale vinde, de regulă, două categorii complet diferite din perspectiva TVA sub același acoperiș: hrană și animale vii, pe de o parte, și accesorii (lese, cuști, jucării, cosmetice) pe de altă parte. Legea le tratează diferit, iar gestiunea de stocuri trebuie organizată astfel încât cota corectă să se aplice automat, pe fiecare produs.

## Temeiul legal

::: ghid-temei
„(2) Cota redusă de 11% se aplică asupra bazei de impozitare pentru următoarele prestări de servicii și/sau livrări de bunuri: [...]
b) livrarea următoarelor bunuri: alimente, inclusiv băuturi, destinate consumului uman și animal, animale și păsări vii din specii domestice, ale căror coduri NC se stabilesc prin normele metodologice, cu excepția: 1. băuturilor alcoolice; 2. băuturilor nealcoolice care se încadrează la codul NC 2202; 3. alimentelor cu zahăr adăugat, al căror conținut total de zahăr este de minimum 10 g/100 g produs, altele decât laptele praf pentru nou-născuți, sugari și copii de vârstă mică; 4. suplimentelor alimentare definite de Legea nr. 56/2021 privind suplimentele alimentare, cu modificările și completările ulterioare;"
— Legea 227/2015 (Codul fiscal), art. 291 alin. (2) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă concret pentru un magazin de animale:

- **Cotă redusă de 11%**: hrana pentru animale (granule, conserve, snack-uri) și animalele/păsările vii din specii domestice — categoria e definită prin coduri NC stabilite în normele metodologice, deci încadrarea unui produs concret la 11% sau nu se verifică pe codul NC al produsului, nu pe denumirea comercială.
- **Cotă standard de 21%**: tot ce nu se încadrează explicit în lista de la alin. (2) — accesorii (lese, zgărzi, cuști, jucării), produse cosmetice pentru animale, servicii de tuns/îngrijit, suplimente alimentare (excluse explicit la lit. b) pct. 4), precum și orice hrană cu zahăr adăugat peste pragul stabilit (pct. 3).
- **Regula generală de încadrare**: dacă un produs nu se regăsește clar în lista limitativă de la art. 291 alin. (2), cota aplicabilă e cea standard — nu se prezumă cota redusă „pentru că e vorba de animale".
- Din perspectiva **gestiunii de stocuri**, asta înseamnă că fiecare produs trebuie introdus în evidență cu cota de TVA proprie, verificată individual — un magazin cu sortiment mixt nu poate aplica o cotă unică pentru tot stocul.

## Ce se greșește în practică

- Se aplică cota de 11% pentru toate produsele din magazin, pe motiv că „e magazin de animale" — cota redusă vizează strict hrana și animalele vii, nu accesoriile sau serviciile conexe.
- Se aplică 11% pentru suplimentele alimentare pentru animale, deși acestea sunt excluse explicit din categoria redusă (pct. 4), fiind tratate distinct de hrana obișnuită.
- Se ignoră verificarea codului NC al produsului la introducerea în stoc, bazându-se doar pe denumirea comercială — două produse cu denumiri similare pot avea coduri NC diferite, deci cote de TVA diferite.

## Ce face iConta.eu

iConta.eu are un modul dedicat de clasificare a cotelor de TVA (`core/cote_tva.py`), care implementează exact distincția din art. 291 alin. (2): o listă limitativă de categorii la cota redusă de 11%, între care „alimente și băuturi pentru consum uman și animal; animale și [păsări vii]", cu tot ce nu se încadrează explicit tratat implicit la cota standard de 21% — regula aplicată e „nu se inventează încadrarea; dacă nu se potrivește clar la 11%, cota e 21%". Contabilul rămâne responsabil să verifice, produs cu produs, dacă acesta se încadrează în categoria redusă (de exemplu, prin codul NC), mai ales pentru produse la limita dintre categorii (suplimente alimentare, hrană cu zahăr adăugat).

[iConta.eu](/)
