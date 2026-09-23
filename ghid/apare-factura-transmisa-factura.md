---
title: "De ce nu apare factura transmisă în e-Factura?"
description: Motive tehnice pentru care o factură emisă pare "netransmisă" — de la eșec de upload, la autentificare expirată la ANAF, la simpla așteptare a unui verdict.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# De ce nu apare factura transmisă în e-Factura?

Când o factură emisă "nu apare" ca transmisă, cauza cea mai frecventă nu este o respingere, ci una din câteva situații tehnice distincte: upload-ul nu a reușit să ajungă la ANAF, autentificarea firmei/cabinetului la ANAF a expirat temporar, sau factura e pur și simplu încă în așteptarea unui verdict.

## Temeiul legal

::: ghid-temei
"În situaţia în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primeşte mesaj cu erorile identificate. După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiaşi sistem naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (5)
:::

Legea acoperă un singur caz concret de "netransmitere": structura facturii nu respectă formatul cerut, situație în care emitentul primește un mesaj cu erorile identificate și trebuie să corecteze și să retrimită. Dincolo de acest caz, distincția între "nu a ajuns la ANAF" și "a ajuns, dar așteaptă verdict" e una tehnică, nu una descrisă explicit de lege.

În practică, o factură poate să nu apară ca "transmisă" din câteva motive diferite:
- upload-ul către ANAF a eșuat la nivel de rețea sau din lipsă de drept pe CIF — în acest caz, factura nu a ajuns deloc în SPV, deci nu are cum să existe un stadiu de validare de urmărit;
- upload-ul a reușit, dar factura e încă în așteptarea unui verdict de la ANAF — aici factura există în SPV, dar procesarea nu s-a încheiat;
- interogarea automată a stadiului nu a putut avea loc pentru că autentificarea (tokenul) folosită pentru accesul la ANAF era temporar expirată sau fără drept — în acest caz nu se marchează factura drept respinsă, ci se reîncearcă interogarea la următoarea rulare programată.

## Ce se greșește în practică

- Se presupune direct că factura a fost respinsă, când de fapt ea încă nu a fost trimisă cu succes către ANAF (eșec de upload) — sunt două situații diferite, cu cauze și remedii diferite.
- Se ignoră faptul că un eșec de autentificare la ANAF (token expirat sau fără drept pe CIF) nu înseamnă că factura a fost respinsă — înseamnă doar că verificarea stadiului nu a putut fi făcută la acea rulare, urmând să fie reîncercată automat.
- Se așteaptă ca factura să apară "transmisă" instant, fără a lua în calcul că verificarea stadiului la ANAF se face periodic, nu în timp real, continuu.

## Ce face iConta.eu

iConta.eu distinge explicit între aceste situații în evidența internă a fiecărei trimiteri: eșecul de upload este marcat separat de starea de "încărcat" (upload reușit) sau de stările ulterioare de procesare. Pentru verificarea periodică a stadiului la ANAF, aplicația folosește autentificarea firmei (sau a cabinetului de contabilitate, dacă factura e administrată prin cabinet) — dacă această autentificare eșuează temporar, rândul respectiv nu este marcat ca respins, ci este sărit la rularea curentă și reinterogat automat la următoarea rulare programată, la 30 de minute.

Menționăm onest o limitare: nu există, în acest moment, un ecran dedicat exclusiv listării facturilor blocate din cauza unei autentificări expirate — pentru diagnosticarea exactă a cauzei pentru care o factură anume nu apare ca transmisă, poate fi nevoie de verificare punctuală.

[iConta.eu](/)
