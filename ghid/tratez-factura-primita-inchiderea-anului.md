---
title: "Cum tratez o factură primită după închiderea anului?"
description: "Ce se schimbă față de o lună obișnuită închisă atunci când factura ținea de un an financiar deja încheiat, și ce mecanism folosește iConta.eu pentru înregistrarea ei."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez o factură primită după închiderea anului?

O factură cu data într-un an deja încheiat urmează același mecanism tehnic ca o factură dintr-o lună închisă — dar, spre deosebire de o simplă lună închisă în cursul anului, aici intervine și problema exercițiului financiar deja raportat.

## Temeiul legal

::: ghid-temei
„Erorile constatate după depunerea situaţiilor financiare anuale se corectează la data constatării lor, potrivit reglementărilor contabile emise de instituţiile prevăzute la art. 4 alin. (1) şi (3), după caz." — Legea nr. 82/1991 (Legea contabilității), art. 36^2
:::

Aceasta e baza legală pentru principiul aplicat de aplicație: o eroare sau o omisiune descoperită după închidere nu se „retroactivează" prin editarea perioadei vechi, ci se corectează la data la care a fost constatată.

## Ce se greșește în practică

- Se tratează o factură din anul închis identic cu una dintr-o lună curentă închisă, fără să se țină cont că, pentru un an financiar deja încheiat (mai ales dacă situațiile financiare au fost deja depuse), nuanța contabilă e diferită față de o simplă lună blocată în cursul anului curent — o distincție documentată separat, pe baza OMFP 1802/2014, în funcție de dacă situațiile financiare au fost depuse și dacă eroarea e semnificativă sau nu.
- Se încearcă forțarea înregistrării direct pe data facturii, într-o lună a anului deja blocat — respinsă de aceeași verificare tehnică folosită pentru orice lună închisă.
- Se presupune că orice factură „uitată" din anul trecut se rezolvă identic, indiferent de mărimea sumei sau de momentul descoperirii — deși tratamentul contabil corect depinde de aceste detalii, nu doar de mecanismul tehnic de blocare.

## Ce face iConta.eu

Tehnic, lunile anului încheiat sunt blocate exact ca orice altă lună închisă: orice încercare de scriere pe o notă contabilă cu data în acea lună e respinsă, indiferent de sursă. Motorul de contare (`contabilizeaza`) acceptă parametrul `data_nota`: dacă luna emiterii facturii e blocată, nota se poate scrie la data descoperirii, în perioada curentă deschisă, cu o mențiune care documentează legătura cu data reală a facturii.

Această regulă tehnică nu înlocuiește însă analiza contabilă pentru un an deja încheiat — dacă situațiile financiare aferente au fost deja depuse, tratamentul corect al erorii (inclusiv dacă afectează sau nu rezultatul reportat) depinde de reglementările contabile aplicabile (OMFP 1802/2014), nu doar de mecanismul de blocare al aplicației. iConta.eu îți permite să înregistrezi factura la data descoperirii, dar încadrarea contabilă corectă a corecției rămâne o decizie care ține cont de aceste reguli.

[iConta.eu](/)
