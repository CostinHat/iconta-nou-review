---
title: "e-Factura rectificativă: când și cum o emiți"
description: O factură rectificativă se emite ori de câte ori o factură deja transmisă la SPV trebuie corectată; iConta.eu o generează prin storno total, fără însă să includă o referință structurată la factura inițială în XML.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# e-Factura rectificativă: când și cum o emiți

„Factură rectificativă" nu e un termen tehnic separat în Codul fiscal — e felul în care se numește, în practică, documentul care modifică o factură deja emisă și transmisă. Legea îi cere un singur lucru esențial: să se refere clar și fără ambiguități la factura pe care o corectează.

## Temeiul legal

::: ghid-temei
„(2) Orice document sau mesaj care modifică și care se referă în mod specific și fără ambiguități la factura inițială are același regim juridic ca o factură." — Cod fiscal 227/2015, art. 319 alin. (2)

„Articolul 330 Corectarea facturilor
(1) Corectarea informațiilor înscrise în facturi sau în alte documente care țin loc de factură se efectuează astfel: […] b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus sau, după caz, o mențiune din care să rezulte că valorile respective sunt negative, iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus […], în care se înscriu numărul și data facturii corectate."

„(21) Facturile emise în sistem simplificat […] trebuie să conțină cel puțin următoarele informații: […] e) […] o referire specifică și clară la factura inițială și la detaliile specifice care se modifică." — Cod fiscal 227/2015, art. 319 alin. (21)
:::

## Când se emite

O rectificativă se emite ori de câte ori o informație dintr-o factură deja transmisă beneficiarului trebuie schimbată: cotă de TVA greșită, cantitate greșită, un produs facturat în plus, un retur. Legea (art. 330 alin. 1 lit. b) dă două variante: fie o singură factură nouă care conține atât valorile negative de corecție, cât și valorile corecte, fie două documente — una cu valori negative (storno) și una nouă, cu valorile corecte.

## Cum o emite iConta.eu — și ce lipsește

iConta.eu implementează varianta „două documente": storno (valori negative, integral, pe toată factura) + o factură nouă separată, creată prin fluxul obișnuit, cu valorile corecte. Documentul de storno se generează automat cu linii negate și descrierea prefixată „STORNO: ".

Punctul unde produsul actual nu acoperă complet cerința legală: art. 319 alin. (2) cere ca documentul rectificativ să se refere „în mod specific și fără ambiguități" la factura inițială, iar alin. (21) lit. e) cere „o referire specifică și clară la factura inițială". Verificat în cod: nu există nicio generare a câmpului structurat de referință (de tipul BillingReference/BT-25) în XML-ul trimis la SPV pentru documentul de storno. Legătura cu factura inițială există doar ca o coloană internă, în baza de date iConta — invizibilă în afara aplicației.

## Ce se greșește în practică

- Se emite storno-ul și se uită emiterea facturii noi, corecte, care completează corecția — storno-ul singur nu „repară" nimic, doar anulează.
- Se presupune că sistemul RO e-Factura sau partenerul comercial vor recunoaște automat legătura dintre rectificativă și originalul ei, din simplul text „STORNO: " din descriere.
- Se încearcă o rectificativă parțială (doar pentru o linie) prin funcția de storno — aceasta anulează întotdeauna 100% din factura originală.
- Nu se documentează separat, manual, corespondența (număr + dată) între factura originală și rectificativă, pentru situațiile în care structura XML nu o poartă.

## Ce face iConta.eu

Pentru corecția unei facturi deja emise, `storneaza()` construiește o factură nouă cu toate liniile originale negate integral, descrierea liniilor prefixată cu „STORNO: ", un număr nou din aceeași serie și data curentă, păstrând moneda/cursul/clasificarea fiscală de pe original. Nota contabilă automată iese cu semn minus prin motorul obișnuit de contare. Corecția propriu-zisă (valorile corecte) se emite ca factură nouă separată, prin fluxul normal de creare. Legătura cu factura originală e păstrată doar intern (`storno_din_id`) — nu există, verificat direct în cod, o generare de referință structurată (BillingReference/InvoiceDocumentReference/BT-25) în XML-ul de e-Factura trimis la SPV.

[iConta.eu](/)
