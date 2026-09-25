---
title: "Cum se descarcă gestiunea pentru ambalaje?"
description: "Conturile prin care iese din gestiune stocul de ambalaje — vânzare, consum, trimitere la terți sau pierderi — potrivit reglementărilor contabile OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se descarcă gestiunea pentru ambalaje?

Ambalajele au propriul grup de conturi în planul de conturi — distinct de mărfuri sau materiale — tocmai pentru că circulă adesea altfel: unele se vând, altele se consumă în procesul de livrare, altele circulă în sistem de restituire către furnizor. Descărcarea din gestiune diferă în funcție de ce se întâmplă efectiv cu ambalajul.

## Temeiul legal

::: ghid-temei
„Contul 381 «Ambalaje» [...] este un cont de activ. [...] În creditul contului 381 «Ambalaje» se înregistrează: – valoarea la preț de înregistrare a ambalajelor vândute ca atare (371); – valoarea la preț de înregistrare a ambalajelor consumate și lipsurile constatate la inventar (608); – valoarea ambalajelor trimise la terți (358); – valoarea la preț de înregistrare a ambalajelor livrate unității sau subunităților (481, 482); – valoarea donațiilor și a pierderilor din calamități (658). Soldul contului reprezintă valoarea la preț de înregistrare a ambalajelor existente în stoc la sfârșitul perioadei."
— OMFP 1802/2014 (Reglementări contabile), Funcțiunea conturilor, Grupa 38 „Ambalaje", contul 381 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din funcțiunea contului rezultă cele patru situații principale în care se descarcă gestiunea de ambalaje:

- **Vânzarea ambalajelor ca atare** (nu odată cu marfa, ci separat, ca produs vândut) — descărcare prin contul **371 „Mărfuri"**.
- **Consumul ambalajelor** în activitatea curentă (ambalarea propriu-zisă a produselor, fără recuperare) și **lipsurile constatate la inventar** — descărcare pe cheltuieli, prin contul **608 „Cheltuieli privind ambalajele"**.
- **Trimiterea ambalajelor la terți** (de exemplu, ambalaje care circulă în sistem de restituire, expediate odată cu marfa către client, urmând să fie restituite) — prin contul **358 „Ambalaje aflate la terți"**.
- **Livrarea către unitate/subunități** ale aceleiași entități — prin conturile **481/482** de decontări intra-entitate; iar **donațiile și pierderile din calamități** se descarcă pe cheltuieli, prin contul **658**.
- Pe partea de intrare (debit), reglementarea menționează separat situația ambalajelor care circulă în sistem de restituire și care **nu au fost restituite furnizorilor**, ci au rămas reținute în stocul propriu — acestea intră în gestiune cu contrapartida contului **409** (avansuri către furnizori/decontări legate de ambalaje).

## Ce se greșește în practică

- Se descarcă toate ambalajele prin contul 608, indiferent dacă au fost vândute, consumate sau doar trimise temporar la client în sistem de restituire — fiecare situație are propriul cont de descărcare, potrivit funcțiunii contului 381.
- Se tratează ambalajele trimise la terți (contul 358) ca fiind definitiv ieșite din patrimoniu, deși ele rămân, contabil, în circuitul firmei până la restituire sau până la decizia de a nu mai fi recuperate.
- Se ignoră contul 388 „Diferențe de preț la ambalaje" atunci când evidența ambalajelor se ține la preț standard, ceea ce duce la o valoare de descărcare incorectă față de costul real de achiziție.

## Ce face iConta.eu

iConta.eu ține evidența stocurilor pe categorii, inclusiv conturile din grupa 38 pentru ambalaje, și generează notele contabile pentru intrările și ieșirile de stoc pe baza documentelor înregistrate (facturi, avize, NIR-uri). Aplicația nu are un flux dedicat separat pentru circuitul ambalajelor care se restituie furnizorilor sau care rămân la terți (contul 358) — alegerea contului corect de descărcare, în funcție de destinația reală a ambalajului, rămâne o decizie a contabilului la fiecare operațiune.

[iConta.eu](/)
