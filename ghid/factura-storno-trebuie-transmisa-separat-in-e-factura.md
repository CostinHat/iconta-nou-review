---
title: Factura storno trebuie transmisă separat în e-Factura?
description: Da — storno-ul e generat ca o factură nouă, cu propriul număr, care intră în fluxul obișnuit de emitere și transmitere; ea nu este trimisă „grupat" cu factura originală, iar legătura dintre ele nu apare structurat în XML.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Factura storno trebuie transmisă separat în e-Factura?

Da. O factură de storno nu e o „adnotare" pe factura originală, ci un document nou, cu numărul lui propriu, care trece prin același circuit ca orice altă factură emisă — inclusiv obligația de transmitere la sistemul RO e-Factura. Important de știut e ce NU face automat sistemul: nu leagă structurat, în XML, noua factură de cea inițială.

## Temeiul legal

::: ghid-temei
„Articolul 330 Corectarea facturilor
(1) Corectarea informațiilor înscrise în facturi sau în alte documente care țin loc de factură se efectuează astfel: […] b) în cazul în care factura a fost transmisă beneficiarului, fie se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus sau, după caz, o mențiune din care să rezulte că valorile respective sunt negative, iar, pe de altă parte, informațiile și valorile corecte, fie se emite o nouă factură conținând informațiile și valorile corecte și concomitent se emite o factură cu valorile cu semnul minus […], în care se înscriu numărul și data facturii corectate."

„r) o referire la alte facturi sau documente emise anterior, atunci când se emit mai multe facturi ori documente pentru aceeași operațiune." — Cod fiscal 227/2015, art. 319 alin. (20)

„(21) Facturile emise în sistem simplificat […] trebuie să conțină cel puțin următoarele informații: […] e) […] o referire specifică și clară la factura inițială și la detaliile specifice care se modifică." — Cod fiscal 227/2015, art. 319 alin. (21)
:::

## Ce înseamnă „separat" în practică

Storno-ul se construiește pe scheletul unei facturi normale: linii noi, cu cantitatea negată, descriere prefixată cu „STORNO: ", un număr nou rezervat din aceeași serie, creat cu data curentă. Pentru că e generat prin exact același mecanism ca o factură emisă obișnuită, el intră în coada de transmitere la SPV ca document distinct — nu există un pas de „trimitere grupată" cu originalul.

Legea (art. 330 alin. 1 lit. b) cere ca noua factură să cuprindă numărul și data facturii corectate. Aceasta e cerința de conținut a documentului de corecție — separată de întrebarea „se trimite separat?" (da), dar strâns legată de ea: dacă documentul se trimite separat, referința la original trebuie să fie vizibilă pe el, nu doar înțeleasă din context.

## Ce se greșește în practică

- Se presupune că storno-ul „merge automat" alături de factura originală într-o singură transmitere la SPV — nu e cazul, sunt două documente distincte.
- Se uită transmiterea efectivă a facturii de storno la SPV, considerând-o o simplă corecție internă.
- Se confundă „anularea" unei facturi netransmise cu „stornarea" uneia deja transmise beneficiarului — legea tratează cele două cazuri diferit (art. 330 alin. 1 lit. a vs. b).
- Se așteaptă ca destinatarul (sau ANAF) să deducă singur legătura dintre storno și original doar din textul „STORNO: " din descrierea liniilor.

## Ce face iConta.eu

Mecanismul real de storno (`storneaza`) refuză operația dacă factura nu are direcția „emisă", apoi construiește linii noi cu cantitatea negată (`-abs(cantitate)`) și descrierea prefixată „STORNO: " + descrierea originală, rezervă un număr nou de factură din aceeași serie și creează documentul cu data de azi, păstrând moneda, cursul și clasificarea fiscală de pe original. Nota contabilă automată iese cu semn minus pe același drum ca orice altă factură emisă, pentru că liniile au cantitate negativă. Legătura cu factura inițială e marcată intern, în baza de date (`storno_din_id`) — verificat: în codul care generează XML-ul de e-Factura nu există nicio referință structurată de tipul BillingReference/BT-25 către factura originală. Documentul de storno se transmite, deci, ca orice factură emisă nouă, dar fără o legătură structurată, vizibilă în XML, către factura pe care o corectează.

[iConta.eu](/)
