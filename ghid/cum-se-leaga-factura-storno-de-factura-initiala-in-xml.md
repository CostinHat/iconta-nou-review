---
title: Cum se leagă factura storno de factura inițială în XML?
description: Nu se leagă — legătura există doar ca o coloană internă în baza de date iConta; XML-ul UBL trimis la SPV nu conține nicio referință structurată (BillingReference/BT-25) către factura corectată.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se leagă factura storno de factura inițială în XML?

Răspunsul scurt, verificat direct din cod: nu se leagă. Factura de storno poartă în descrierea fiecărei linii prefixul „STORNO: ", dar acest text nu e o referință structurată pe care sistemul RO e-Factura sau un ERP terț o poate citi automat. Legătura reală există doar în baza de date internă a iConta.

## Temeiul legal

::: ghid-temei
„r) o referire la alte facturi sau documente emise anterior, atunci când se emit mai multe facturi ori documente pentru aceeași operațiune." — Cod fiscal 227/2015, art. 319 alin. (20)

„(21) Facturile emise în sistem simplificat […] trebuie să conțină cel puțin următoarele informații: […] e) în cazul documentelor sau mesajelor tratate drept factură în conformitate cu prevederile alin. (2), o referire specifică și clară la factura inițială și la detaliile specifice care se modifică." — Cod fiscal 227/2015, art. 319 alin. (21)

„(2) Orice document sau mesaj care modifică și care se referă în mod specific și fără ambiguități la factura inițială are același regim juridic ca o factură." — Cod fiscal 227/2015, art. 319 alin. (2)

„Articolul 330 Corectarea facturilor (1) […] b) […] se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus […]" — Cod fiscal 227/2015, art. 330
:::

## Ce spune legea față de ce face motorul

Legea cere, explicit, ca documentul de corecție să conțină „numărul și data facturii corectate" (art. 330 alin. 1 lit. b) și „o referire specifică și clară la factura inițială" (art. 319 alin. 21 lit. e). Standardul tehnic pentru e-Factura (formatul UBL/CIUS-RO folosit de SPV) are exact un câmp dedicat pentru asta — de tipul BillingReference/InvoiceDocumentReference (cunoscut și ca elementul BT-25 în schema europeană) — prin care factura de corecție indică numărul și data documentului pe care îl corectează.

În codul verificat, acest câmp nu e populat. O căutare pe tot motorul de facturare pentru orice generare de BillingReference, InvoiceDocumentReference sau BT-25 nu găsește niciun rezultat. Cu alte cuvinte: XML-ul transmis la SPV pentru o factură de storno nu poartă, structurat, informația despre factura originală — doar textul liber „STORNO: " în descrierea liniilor, care nu are valoare de referință tehnică.

## Ce se greșește în practică

- Se presupune că prefixul „STORNO: " din descriere echivalează, legal și tehnic, cu o referință structurată la factura inițială — nu echivalează.
- Se caută în XML-ul descărcat din SPV un câmp BillingReference care, pentru facturile de storno emise din sistem, pur și simplu nu există.
- Se consideră suficientă legătura din baza de date internă (`storno_din_id`) pentru un control ANAF sau pentru un audit extern — aceasta e invizibilă în afara aplicației.
- Nu se păstrează, separat, o evidență manuală (număr + dată factură originală) în cazurile în care referința structurată contează pentru documentarea corecției.

## Ce face iConta.eu

`storneaza()` citește factura originală, refuză operația dacă factura nu are direcția „emisă", construiește linii noi cu cantitatea negată și descrierea prefixată „STORNO: " + descrierea originală, rezervă un număr nou din aceeași serie și creează documentul cu data curentă. Singura legătură persistentă cu factura originală e coloana internă `storno_din_id` din baza de date — o legătură vizibilă în aplicație, dar nu pe documentul emis și nu în XML-ul transmis la SPV. Verificat direct în codul care generează structura de e-Factura: nu există nicio generare de BillingReference, InvoiceDocumentReference sau echivalentul BT-25. Aceasta e o limitare cunoscută a motorului curent, nu un comportament ascuns.

[iConta.eu](/)
