---
title: Când pot deduce pierderea dintr-o creanță neîncasată?
description: Pierderea din scoaterea din evidență a unei creanțe e deductibilă, pentru partea neacoperită de ajustare, doar în șase situații expres prevăzute (reorganizare judiciară, faliment închis, decesul debitorului, dizolvare/lichidare fără succesor, dificultăți financiare majore, asigurare).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Când pot deduce pierderea dintr-o creanță neîncasată?

Ajustarea pentru deprecierea creanțelor (constituirea provizionului) e un pas intermediar — reflectă riscul de neîncasare, dar creanța rămâne în evidență. Scoaterea efectivă din evidență a creanței (atunci când devine clar că nu mai poate fi recuperată) e o operațiune distinctă, cu propriul regim de deductibilitate, care nu se confundă cu regimul ajustării.

## Temeiul legal

::: ghid-temei
"h) pierderile înregistrate la scoaterea din evidență a creanțelor, pentru partea neacoperită de
provizion, potrivit art. 26, precum și cele înregistrate în alte cazuri decât următoarele:
1. punerea în aplicare a unui plan de reorganizare confirmat printr-o sentință judecătorească, în
conformitate cu prevederile Legii nr. 85/2014;
2. procedura de faliment a debitorilor a fost închisă pe baza hotărârii judecătorești;
3. debitorul a decedat și creanța nu poate fi recuperată de la moștenitori;
4. debitorul este dizolvat, în cazul societății cu răspundere limitată cu asociat unic, sau lichidat,
fără succesor;
5. debitorul înregistrează dificultăți financiare majore care îi afectează întreg patrimoniul;
6. au fost încheiate contracte de asigurare;"
:::

## Cum se citește textul

Formularea legii e o dublă negație, ușor de citit greșit: pierderea la scoaterea din evidență a creanței, pentru partea **neacoperită de ajustare**, e nedeductibilă **cu excepția** celor 6 cazuri enumerate. Cu alte cuvinte, pierderea e deductibilă doar dacă te încadrezi în unul din cele șase puncte — altfel rămâne cheltuială nedeductibilă, oricât de clar e că suma nu va mai fi recuperată.

::: ghid-exemplu
O creanță de 15.000 lei are constituită o ajustare deductibilă de 4.500 lei (30%, conform art. 26 lit. c)). Debitorul intră în faliment, iar procedura se închide prin hotărâre judecătorească. La scoaterea creanței din evidență, partea neacoperită de ajustare (10.500 lei) e deductibilă, pentru că situația se încadrează la punctul 2 (faliment închis). Dacă în schimb firma renunță pur și simplu la recuperare, fără niciunul din cele 6 temeiuri, cei 10.500 lei rămân cheltuială nedeductibilă.
:::

## Ce se greșește în practică

- Se confundă constituirea ajustării (cont 491, art. 26) cu scoaterea efectivă din evidență a creanței (art. 25 alin. (4) lit. h)) — sunt două operațiuni și două regimuri fiscale diferite.
- Se scoate creanța din evidență și se deduce integral pierderea doar pentru că a trecut mult timp, fără să existe unul din cele 6 temeiuri legale.
- Se presupune că "dificultăți financiare majore" (punctul 5) înseamnă orice întârziere la plată — legea cere ca acestea să afecteze întregul patrimoniu al debitorului, un prag mult mai ridicat.
- Se uită partea deja acoperită de ajustare — doar diferența neacoperită intră în analiza de deductibilitate de la lit. h); partea acoperită de ajustare a fost deja tratată fiscal la constituirea acesteia.

## Ce face iConta.eu

`core/provizioane.py` acoperă doar constituirea și reluarea ajustării pentru deprecierea creanțelor (`nota_ajustare_creanta`, cu notele contabile 6814=491 la constituire și 491=7814 la reluare) — motorul nu modelează operațiunea de scoatere din evidență a creanței (înregistrarea pierderii propriu-zise, de regulă pe 654=411 sau 659=411, pentru partea neacoperită) și nu verifică niciunul din cele 6 temeiuri de mai sus. Încadrarea într-un caz din cele 6 și calculul deductibilității pierderii rămân integral în sarcina utilizatorului.

[iConta.eu](/)
