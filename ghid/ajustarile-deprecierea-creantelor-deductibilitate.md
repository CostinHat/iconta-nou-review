---
title: "Ajustările pentru deprecierea creanțelor: deductibilitate"
description: "Deductibilitatea ajustărilor pentru deprecierea creanțelor se stabilește prin verificarea, în ordine, a garantării, afilierii, stadiului de faliment/insolvență și, în lipsa acestuia, a numărului de zile de la scadență."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ajustările pentru deprecierea creanțelor: deductibilitate

Deductibilitatea unei ajustări pentru deprecierea creanțelor nu se stabilește dintr-o singură verificare, ci dintr-o secvență: mai întâi garantarea și afilierea creanței, care pot exclude deducerea complet, apoi stadiul de faliment/insolvență al debitorului, și, în lipsa acestuia, vechimea creanței de la data scadenței.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] c) ajustările pentru deprecierea creanțelor [...] în limita unui procent de 30% din valoarea acestor ajustări [...] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței; 2. nu sunt garantate de altă persoană; 3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului."

*(Codul fiscal — Legea nr. 227/2015, art. 26 alin. (1) lit. c))*
:::

## Structura verificării

- **Garantare sau afiliere** → dacă oricare e prezentă, deducerea e 0%, indiferent de vechimea creanței sau de stadiul debitorului.
- **Faliment declarat (persoană juridică) sau insolvență (persoană fizică)** → deducere 100% (art. 26 alin. (1) lit. j)), fără prag de zile, cu condiția negarantării și neafilierii.
- **În lipsa falimentului/insolvenței, peste 270 de zile de la scadență** → deducere 30% (art. 26 alin. (1) lit. c)), tot cu condiția negarantării și neafilierii.
- **Sub 270 de zile, fără faliment declarat** → 0%, pragul nefiind încă atins.

Cheltuiala de constituire a ajustării (6814) e ea însăși încadrată la cheltuieli cu deductibilitate limitată (art. 25 alin. (3) lit. g), „în limita prevăzută la art. 26"), deci procentul stabilit mai sus se aplică direct asupra cheltuielii înregistrate contabil.

## Ce se greșește în practică

- Se deduce ajustarea integral, fără verificarea prealabilă a garantării și afilierii creanței.
- Se aplică pragul de 270 de zile și în cazul debitorilor aflați deja în faliment declarat, unde deducerea corectă e 100%, imediată.
- Se confundă ajustarea (constituirea 491, deductibilă condiționat) cu pierderea efectivă la scoaterea din evidență a creanței (art. 25 alin. (4) lit. h), regim separat, condiționat de alte șase situații).

## Ce face iConta.eu

`deductibilitate_creanta(zile_depasire_scadenta, garantata, afiliata, faliment_declarat)` din `core/provizioane.py` parcurge exact această ordine de verificare și generează nota `6814=491` pentru constituire. Aplicația nu calculează automat numărul de zile de întârziere sau stadiul procedurii de insolvență a debitorului — aceste date se introduc manual, pe baza documentelor firmei.

[iConta.eu](/)
