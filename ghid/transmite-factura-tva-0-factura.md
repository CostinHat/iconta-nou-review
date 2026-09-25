---
title: "Cum se transmite o factură cu TVA 0 în e-Factura"
description: "Cum se clasifică pe factură o operațiune cu cotă de TVA 0% (export, livrare intracomunitară) și cum ajunge această clasificare în XML-ul transmis prin RO e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se transmite o factură cu TVA 0 în e-Factura

O factură cu „TVA 0" nu înseamnă că taxa a fost omisă, ci că operațiunea e scutită de TVA cu drept de deducere — cel mai frecvent, un export sau o livrare intracomunitară de bunuri. Clasificarea corectă a operațiunii pe factură decide atât rândul din decontul de TVA, cât și categoria de cotă pe care o vede ANAF în XML-ul transmis prin RO e-Factura.

## Temeiul legal

::: ghid-temei
„Articolul 294 [...] (1) Sunt scutite de taxă: a) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către furnizor sau de altă persoană în contul său; [...]
(2) Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă sau către o persoană juridică neimpozabilă care acționează ca atare în alt stat membru decât cel în care începe expedierea sau transportul bunurilor, care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru [...]"
— Codul fiscal (Legea 227/2015), art. 294 alin. (1) lit. a) și alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se leagă temeiul legal de clasificarea pe factură și de XML-ul e-Factura:

- Operațiunea se clasifică pe factură prin **țara terțului** (client/furnizor din UE sau din afara UE) și prin **tipul operațiunii intracomunitare** (bunuri/servicii) — aceste câmpuri decid dacă operațiunea e un export, o livrare intracomunitară scutită conform art. 294, sau o livrare internă obișnuită.
- Cota de TVA aplicată efectiv liniei de factură rămâne **0%**, corespunzător scutirii — nu se „ascunde" cota, ci se marchează explicit ca zero.
- În XML-ul UBL/CIUS-RO transmis prin RO e-Factura, categoria de TVA a liniei devine **„Z" (cotă zero)** atunci când cota facturii e 0 — categorie distinctă de „S" (cotă standard), folosită pentru operațiunile taxabile obișnuite.
- **Atenție la o distincție tehnică reală**: categoria „Z" (cotă zero) nu e același lucru cu categoria „E" (scutit, cu cod de motiv al scutirii — de exemplu, o scutire fără drept de deducere). O factură cu TVA 0% pentru export/livrare IC se transmite corect ca „Z"; un cod de motiv explicit al scutirii, cerut de standardul european pentru categoria „E", e altceva.

## Ce se greșește în practică

- Se emite factura cu cota de TVA lăsată necompletată sau ambiguă, în loc de 0% explicit — riscând ca XML-ul generat să nu reflecte corect categoria „cotă zero".
- Se presupune că „TVA 0" și „scutit de TVA cu motiv explicit" sunt aceeași categorie tehnică în e-Factura — de fapt standardul UBL le tratează diferit (Z vs. E, cu cod de motiv).
- Se completează câmpul de clasificare a operațiunii (țară terț, tip IC) abia după emitere, când de fapt el trebuie stabilit corect chiar la introducerea facturii, pentru ca atât rândul din D300, cât și XML-ul e-Factura să pornească de la aceeași informație.

## Ce face iConta.eu

Clasificarea operațiunii se face la introducerea facturii, din câmpurile „țara terțului" și tipul de operațiune intracomunitară (`core/facturi_api.py`), aceleași câmpuri care rutează corect rândul din D300 (livrări IC, export). La generarea XML-ului pentru RO e-Factura (`core/efactura_send.py`), categoria de TVA a fiecărei linii se stabilește automat din cota facturii: cotă peste zero → categoria „S" (standard), cotă zero → categoria „Z" — deci o factură cu TVA 0% (export sau livrare intracomunitară) se transmite corect, cu categoria potrivită, fără intervenție suplimentară.

O limită reală, de reținut: generatorul actual **nu emite categoria „E" (scutit, cu motiv explicit/VATEX)** și nu are un câmp dedicat pentru codul de motiv al scutirii — doar distincția standard (S) / cotă zero (Z). Pentru operațiunile la care e nevoie strict de mențiunea „scutit conform art. X", nu doar de cota zero, acest detaliu nu e susținut încă în XML-ul generat.

[iConta.eu](/)
