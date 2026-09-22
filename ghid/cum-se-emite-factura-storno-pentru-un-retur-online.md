---
title: Cum se emite factura storno pentru un retur online?
description: Storno-ul din iConta.eu se generează automat, ca o factură nouă cu liniile negate integral, la data curentă; pentru un retur online parțial, e nevoie de o factură de corecție creată manual, pentru că motorul nu susține stornarea parțială.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se emite factura storno pentru un retur online?

Pentru un retur online complet — clientul returnează tot ce a comandat — funcția de storno din iConta.eu automatizează corect mecanica stornării integrale, dar cu aceleași limite de an fiscal și referință XML ca orice storno din iConta: nu verifică dacă factura originală a rămas în același exercițiu financiar, iar legătura cu factura originală nu apare structurat în XML-ul trimis la SPV. Pentru un retur parțial, situația e diferită, și merită înțeleasă înainte să apeși butonul.

## Temeiul legal

::: ghid-temei
„Articolul 330 Corectarea facturilor
(1) Corectarea informațiilor înscrise în facturi sau în alte documente care țin loc de factură se efectuează astfel: […] b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus sau, după caz, o mențiune din care să rezulte că valorile respective sunt negative, iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus […], în care se înscriu numărul și data facturii corectate."

„69. ‐ Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roşu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă şi programele informatice utilizate." — OMFP 1802/2014, pct. 69
:::

## Pas cu pas: ce face storno-ul

Când se cere stornarea unei facturi emise pentru un retur online:

1. Sistemul verifică factura originală și refuză operația dacă factura nu are direcția „emisă" (nu se pot storna facturi primite pe această cale).
2. Construiește linii noi, cu cantitatea negată pentru fiecare produs din comandă, și descrierea prefixată cu „STORNO: " urmată de descrierea originală.
3. Rezervă un număr nou de factură, din aceeași serie ca originalul.
4. Creează documentul cu data de azi — nu cu data facturii originale — dar păstrează moneda, cursul de schimb și clasificarea fiscală (taxare inversă, tranzacție intracomunitară, categoria operațiunii, data faptului generator) de pe factura inițială.
5. Marchează intern legătura cu factura originală.

Pentru că liniile au cantitate negativă, nota contabilă automată iese cu semn minus prin același drum ca orice altă factură emisă — exact mecanica descrisă la pct. 69: corectarea prin semnul minus, aplicată operațiunii curente.

## Ce se greșește în practică

- Se folosește storno-ul pentru un retur parțial (un singur produs dintr-o comandă cu mai multe), deși el anulează întreaga factură, nu doar produsul returnat.
- Se ignoră faptul că factura de storno poartă data emiterii ei, nu data comenzii originale — relevant dacă returul vine peste granița dintre două luni sau exerciții fiscale.
- Nu se retransmite clientul cu factura de storno la SPV/RO e-Factura, considerând-o o simplă corecție internă.
- Se presupune că sistemul leagă automat, în documentul trimis clientului sau la ANAF, factura de storno de comanda/factura originală — legătura structurată nu există în afara bazei de date interne.

## Ce face iConta.eu

`storneaza()` implementează exact pașii descriși mai sus: citește factura originală, refuză dacă direcția nu e „emisă", construiește linii cu cantitatea negată și descrierea prefixată, rezervă un număr nou și creează documentul cu data curentă, păstrând moneda/cursul/clasificarea de pe original. Nota automată se generează cu semn minus prin motorul obișnuit de contare (`genereaza_note` → `factura_emisa`), nu printr-o funcție separată de inversare a unei note deja scrise. Stornarea e întotdeauna totală — toate liniile facturii originale sunt negate integral, fără opțiune de a selecta doar unele. Pentru un retur parțial dintr-o comandă online, singura variantă corectă e o factură de corecție construită manual, cu liniile exacte ale returului, nu funcția de storno.

[iConta.eu](/)
