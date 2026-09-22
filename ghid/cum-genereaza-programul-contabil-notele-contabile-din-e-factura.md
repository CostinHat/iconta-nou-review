---
title: Cum generează programul contabil notele contabile din e-Factura?
description: Facturile emise se contabilizează automat, în aceeași tranzacție cu emiterea; facturile primite se contabilizează abia la validare, iar cele intrate prin import SPV/XML rămân necontate.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum generează programul contabil notele contabile din e-Factura?

Generarea notei contabile nu e un pas separat, pe care contabilul trebuie să-l declanșeze manual după fiecare factură. iConta.eu leagă contarea de momentul faptului economic, dar acest moment nu e același pentru facturile emise și pentru cele primite — iar facturile care intră prin import din SPV au un regim aparte, documentat explicit ca limitare.

## Temeiul legal

::: ghid-temei
„4426. TVA deductibilă (A)
4427. TVA colectată (P)
4428. TVA neexigibilă (A/P)" — OMFP 1802/2014

„401. Furnizori (P)" / „4111. Clienți (A)" — OMFP 1802/2014

„Articolul 282 Exigibilitatea pentru livrări de bunuri și prestări de servicii
(1) Exigibilitatea taxei intervine la data la care are loc faptul generator.
(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: a) la data emiterii unei facturi, înainte de data la care intervine faptul generator; […]" — Cod fiscal 227/2015, art. 282
:::

## Când se scrie efectiv nota

Pentru o **factură emisă** de tip „factură" (nu proformă, nu aviz), nota se scrie automat, în aceeași tranzacție cu crearea facturii. Dacă emiterea eșuează mai târziu din orice motiv (de exemplu cursul BNR nu poate fi obținut), nota cade odată cu factura — nu rămâne o notă „orfană" fără document.

Pentru o **factură primită**, faptul economic relevant nu e sosirea documentului, ci recunoașterea cheltuielii de către contabil — de aceea nota se scrie abia la validarea facturii, nu la înregistrarea ei în sistem.

Facturile intrate prin **import SPV/XML** rămân necontate. Nu e un bug ascuns, ci o limitare cunoscută și documentată: importul aduce documentul în sistem, dar nu declanșează automat generarea notei contabile.

Pe fiecare linie sau grup de linii cu aceeași cotă de TVA se calculează separat baza și taxa — nu pe totalul facturii. Asta contează concret pentru facturile mixte, cu produse la 21% și servicii la 11% (sau orice combinație de cote): dacă nota s-ar calcula pe total, rotunjirile ar putea deraia suma de TVA colectată/deductibilă față de cea reală.

::: ghid-exemplu
O factură cu o linie de marfă (cota standard) și o linie de servicii (cotă redusă) generează două calcule de TVA distincte, unul per grup de cotă, apoi le însumează în aceeași notă — nu se calculează un TVA „mediu" pe totalul facturii.
:::

## Ce se greșește în practică

- Se așteaptă ca o factură primită să apară deja contată imediat ce e vizibilă în sistem — de fapt, nota apare abia după validare.
- Se presupune că facturile importate din SPV sunt contate automat, ca orice factură emisă — nu sunt; rămân necontate până la o acțiune explicită.
- Se calculează manual TVA-ul pe totalul facturii, în loc de pe fiecare cotă separat, la facturile cu produse/servicii taxate diferit.
- Nu se verifică statusul facturii (anulată/stornată) atunci când se caută o notă lipsă — un document „void" nu produce, corect, niciun fapt economic și deci nicio notă.

## Ce face iConta.eu

La crearea unei facturi emise de tip factură, `creeaza_factura` apelează, în aceeași tranzacție, `_conteaza_la_creare`, care declanșează motorul de contare (`contare_facturi.genereaza_note`). Pentru facturile primite, contarea e amânată la acțiunea de validare (decizie internă R88), tocmai pentru că faptul economic e recunoașterea cheltuielii, nu primirea documentului. `genereaza_note` calculează baza și TVA-ul pe fiecare linie/grup de cotă în parte, nu pe totalul facturii — o corecție explicită pentru facturile mixte. O notă e recunoscută ca „notă de contare" doar dacă atinge un cont de terț (4111/401/404) și fondul sau TVA-ul, fără să atingă trezoreria — definiție folosită și pentru a evita scrierea de două ori a aceleiași note. O factură anulată sau stornată nu primește notă, iar o factură în valută fără curs BNR disponibil nu se contează.

[iConta.eu](/)
