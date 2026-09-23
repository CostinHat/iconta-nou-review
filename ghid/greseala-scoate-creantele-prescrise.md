---
title: "Greșeala de a nu scoate creanțele prescrise"
description: "A lăsa în evidență o creanță prescrisă nu e doar o problemă contabilă — la impozitul pe profit, pierderea din scoaterea ei din evidență e nedeductibilă, cu excepția a șase situații enumerate expres, iar prescripția în sine nu se numără printre ele."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeala de a nu scoate creanțele prescrise

A lăsa o creanță prescrisă în continuare în evidență, fără să fie scoasă la momentul potrivit, complică ulterior justificarea fiscală a pierderii. Dar chiar și scoasă corect din evidență, pierderea rămasă neacoperită de provizion nu e automat deductibilă — legea o deduce doar dacă situația se încadrează în una din cele șase cazuri enumerate expres, iar simpla prescripție nu e una dintre ele.

## Temeiul legal

::: ghid-temei
„Următoarele cheltuieli nu sunt deductibile: [...] h) pierderile înregistrate la scoaterea din evidență a creanțelor, pentru partea neacoperită de provizion, potrivit art. 26, precum și cele înregistrate în alte cazuri decât următoarele: 1. punerea în aplicare a unui plan de reorganizare confirmat printr-o sentință judecătorească [...]; 2. procedura de faliment a debitorilor a fost închisă pe baza hotărârii judecătorești; 3. debitorul a decedat și creanța nu poate fi recuperată de la moștenitori; 4. debitorul este dizolvat, în cazul societății cu răspundere limitată cu asociat unic, sau lichidat, fără succesor; 5. debitorul înregistrează dificultăți financiare majore care îi afectează întreg patrimoniul; 6. au fost încheiate contracte de asigurare."

*(Codul fiscal — Legea nr. 227/2015, art. 25 alin. (4) lit. h))*
:::

## Ce înseamnă practic pentru o creanță prescrisă

Regula de bază: pierderea la scoaterea din evidență a unei creanțe e nedeductibilă, cu excepția celor șase cazuri enumerate. Prescripția extinctivă (dreptul de a cere executarea silită s-a stins) **nu apare** printre cele șase situații — deci, dacă motivul scoaterii din evidență e strict prescripția, fără să existe și una din cele șase condiții (de exemplu debitorul dizolvat fără succesor, sau în dificultăți financiare majore care îi afectează întreg patrimoniul), pierderea rămâne, în principiu, nedeductibilă.

Dacă pentru creanța respectivă a fost constituită anterior o ajustare (491), dedusă parțial sau integral conform art. 26, partea deja dedusă nu se dublează la scoaterea din evidență — regula de la lit. h) vizează doar partea neacoperită de provizion.

## Ce se greșește în practică

- Se lasă creanța prescrisă în evidență la nesfârșit, fără nicio scoatere, ceea ce distorsionează balanța și expune firma la riscuri de raportare.
- Se scoate creanța din evidență și se deduce integral pierderea, considerând prescripția suficientă, fără verificarea celor șase condiții din art. 25 alin. (4) lit. h).
- Se ignoră faptul că partea deja acoperită de o ajustare dedusă anterior (art. 26) nu se recalculează sau se dublează la scoaterea din evidență.

## Ce face iConta.eu

`core/provizioane.py` calculează și contabilizează ajustarea deductibilă a creanțelor (`deductibilitate_creanta`, art. 26), dar nu modelează scoaterea propriu-zisă din evidență a unei creanțe și nu verifică dacă situația concretă se încadrează în una din cele șase excepții de la art. 25 alin. (4) lit. h) — aceasta rămâne o evaluare manuală a contabilului, pe baza documentelor disponibile despre debitor.

[iConta.eu](/)
