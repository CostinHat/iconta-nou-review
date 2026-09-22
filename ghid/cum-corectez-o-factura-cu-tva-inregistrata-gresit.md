---
title: Cum corectez o factură cu TVA înregistrată greșit?
description: Legal, o factură netransmisă beneficiarului s-ar putea anula direct — dar în iConta.eu ștergerea e refuzată pentru orice factură deja creată, pentru că nota de contare se scrie automat la emitere; corectarea trece mereu prin storno total plus emiterea unei facturi noi, corecte — iConta.eu nu oferă corecția directă a unei singure linii cu TVA greșit.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectez o factură cu TVA înregistrată greșit?

O cotă de TVA greșită pe o factură deja emisă nu se poate „edita" pe loc — nici legal, nici tehnic, în iConta.eu. Calea de corecție depinde de un singur lucru: dacă factura a ajuns deja la client sau nu.

## Temeiul legal

::: ghid-temei
„Articolul 330 Corectarea facturilor
(1) Corectarea informațiilor înscrise în facturi sau în alte documente care țin loc de factură se efectuează astfel: a) în cazul în care factura nu a fost transmisă către beneficiar, aceasta se anulează și se emite o nouă factură; b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus sau, după caz, o mențiune din care să rezulte că valorile respective sunt negative, iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus […], în care se înscriu numărul și data facturii corectate."

„4426. TVA deductibilă (A)
4427. TVA colectată (P)
4428. TVA neexigibilă (A/P)" — OMFP 1802/2014
:::

## Cele două căi, și de ce iConta.eu oferă doar una

Legea distinge clar: dacă factura n-a ajuns încă la client, se anulează pur și simplu și se emite alta, corectă (art. 330 alin. 1 lit. a). Dacă a ajuns deja la client, trebuie fie o factură de corecție cu valorile corecte, fie storno (valori cu minus) urmat de o factură nouă, corectă (alin. 1 lit. b).

În iConta.eu, ștergerea unei facturi emise e refuzată din momentul în care are notă de contare atașată — iar pentru facturile emise de tip factură, nota se scrie automat, în aceeași tranzacție cu crearea documentului. Practic, pentru orice factură deja creată în sistem (nu doar deja trimisă clientului), varianta „anulare simplă" nu mai e disponibilă prin ștergere — sistemul direcționează explicit spre storno, ca să nu rămână o notă contabilă „orfană", fără document.

Asta înseamnă că o factură cu o cotă de TVA greșită pe o singură linie se corectează prin storno **total**, urmat de emiterea unei facturi noi, cu toate liniile — inclusiv cele care erau deja corecte — reintroduse cu cota corectă. Nu există o corecție „chirurgicală" doar a liniei greșite.

::: ghid-exemplu
O factură cu 3 linii, dintre care una a fost înregistrată cu cota standard în loc de cota redusă aplicabilă. Corectarea nu înseamnă modificarea acelei linii, ci: storno total al facturii (toate cele 3 linii, cu semn minus) + o factură nouă, cu toate cele 3 linii reintroduse, de data asta cu cota corectă pe linia greșită.
:::

Dacă firma sau furnizorul e la TVA la încasare, atenție și la contul folosit: baza merge normal pe contul de venit/achiziție, dar TVA-ul poate merge pe 4428 (neexigibilă) în loc de 4427/4426, în funcție de regim — o eroare de cotă poate fi însoțită și de o eroare de cont, dacă regimul de TVA la încasare nu a fost luat corect în calcul la emitere.

## Ce se greșește în practică

- Se încearcă „editarea" cotei de TVA direct pe o factură deja emisă și contată — sistemul nu permite acest lucru.
- Se așteaptă o corecție doar a liniei greșite; de fapt storno-ul anulează întreaga factură.
- Se uită să se retrimită factura nouă, corectă, clientului și la SPV, după storno.
- Nu se verifică dacă eroarea de TVA a afectat și contul folosit (4426/4427 vs. 4428), în cazul facturilor cu regim de TVA la încasare.
- Nu se păstrează, separat de aplicație, o referință clară (număr + dată) între factura greșită și cea corectă, dat fiind că XML-ul de e-Factura nu poartă această legătură structurat.

## Ce face iConta.eu

`sterge_factura` refuză ștergerea unei facturi cu notă de contare atașată și direcționează explicit spre storno, ca să nu rămână o „gaură" în evidență. Pentru facturi deja create/emise, corectarea unei cote de TVA greșite trece prin `storneaza()`: negarea integrală a tuturor liniilor facturii originale, urmată de crearea unei facturi noi, cu liniile corecte, prin fluxul normal de creare. `genereaza_note` calculează baza și TVA-ul pe fiecare linie/grup de cotă separat, ceea ce asigură că factura nouă, corectă, calculează exact TVA-ul pe fiecare cotă din nou. Stornarea rămâne totală — nu există corecție parțială doar a liniei greșite — iar legătura dintre factura greșită și cea corectă nu apare structurat în XML-ul transmis la SPV, doar în baza de date internă.

[iConta.eu](/)
