---
title: "Cheltuieli cu creanțele neîncasate: când sunt deductibile"
description: "Două cheltuieli diferite, două regimuri diferite — ajustarea contabilă (deductibilă condiționat, 30% sau 100%) și pierderea la scoaterea din evidență a creanței (deductibilă doar în șase situații enumerate expres)."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cheltuieli cu creanțele neîncasate: când sunt deductibile

O creanță neîncasată poate genera două cheltuieli distincte, fiecare cu propriul regim de deductibilitate: cheltuiala cu ajustarea pentru depreciere, constituită cât timp creanța există încă în evidență, și cheltuiala cu pierderea propriu-zisă, la momentul la care creanța e scoasă definitiv din evidență. Cele două nu se confundă și nu au aceleași condiții.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] c) ajustările pentru deprecierea creanțelor [...] în limita unui procent de 30% [...] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței; 2. nu sunt garantate de altă persoană; 3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului. [...]

Următoarele cheltuieli nu sunt deductibile: [...] h) pierderile înregistrate la scoaterea din evidență a creanțelor, pentru partea neacoperită de provizion, potrivit art. 26, precum și cele înregistrate în alte cazuri decât următoarele: 1. punerea în aplicare a unui plan de reorganizare confirmat printr-o sentință judecătorească [...]; 2. procedura de faliment a debitorilor a fost închisă pe baza hotărârii judecătorești; 3. debitorul a decedat și creanța nu poate fi recuperată de la moștenitori; 4. debitorul este dizolvat [...] sau lichidat, fără succesor; 5. debitorul înregistrează dificultăți financiare majore care îi afectează întreg patrimoniul; 6. au fost încheiate contracte de asigurare."

*(Codul fiscal — Legea nr. 227/2015, art. 26 alin. (1) lit. c) și art. 25 alin. (4) lit. h))*
:::

## Cele două momente, cele două regimuri

1. **Cât timp creanța e încă în evidență** — cheltuiala cu ajustarea (6814) e deductibilă la 30% (peste 270 de zile, negarantată, neafiliată) sau la 100% (faliment declarat/insolvență, negarantată, neafiliată); în rest, 0%.
2. **La scoaterea din evidență a creanței** — pierderea rămasă, pentru partea neacoperită de ajustarea deja dedusă, e deductibilă **doar** dacă situația se încadrează în una din cele șase excepții enumerate la art. 25 alin. (4) lit. h) (reorganizare confirmată, faliment închis, decesul debitorului fără moștenitori recuperabili, dizolvare/lichidare fără succesor, dificultăți financiare majore ale debitorului, sau existența unui contract de asigurare). În afara acestor situații, pierderea la scoaterea din evidență rămâne nedeductibilă.

## Ce se greșește în practică

- Se deduce integral pierderea la scoaterea din evidență, fără verificarea celor șase condiții din art. 25 alin. (4) lit. h).
- Se dublează deducerea: se scade din nou, la scoaterea din evidență, partea deja dedusă anterior prin ajustarea de 30%/100%.
- Se tratează ajustarea (491) și pierderea la scoatere din evidență ca fiind aceeași operațiune fiscală, deși au condiții de deductibilitate diferite.

## Ce face iConta.eu

`core/provizioane.py` calculează și contabilizează doar ajustarea (constituire 6814=491, reluare 491=7814), pe baza `deductibilitate_creanta`. Aplicația nu modelează scoaterea propriu-zisă din evidență a creanței și nu verifică încadrarea în cele șase excepții de la art. 25 alin. (4) lit. h) — această evaluare, la fel ca și nota contabilă corespunzătoare, rămâne manuală.

[iConta.eu](/)
