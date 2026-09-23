---
title: "Cum se înregistrează dobânda la creditul bancar"
description: "Explică modul de contabilizare a dobânzii la creditele bancare clasice, pe termen lung și pe termen scurt, de la angajarea lunară până la plată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează dobânda la creditul bancar

Pentru un credit bancar clasic (nu descoperit de cont), dobânda se înregistrează în doi pași: angajarea lunară a dobânzii datorate și, ulterior, plata ei efectivă.

## Temeiul legal

::: ghid-temei
"Contul 168 «Dobânzi aferente împrumuturilor și datoriilor asimilate» [...] este un cont de pasiv. În creditul contului 168 [...] se înregistrează: – valoarea dobânzilor datorate, aferente împrumuturilor și datoriilor asimilate (666); [...] În debitul contului 168 [...] se înregistrează: – suma dobânzilor plătite aferente împrumuturilor și datoriilor asimilate (512); [...] Soldul contului reprezintă dobânzile datorate și neplătite." — OMFP 1802/2014, monografia contului 168

"Cu ajutorul acestui cont [519] se ține evidența creditelor acordate de bănci pe termen scurt. [...] 5198. Dobânzi aferente creditelor bancare pe termen scurt (P)" — OMFP 1802/2014, monografia și planul de conturi al contului 519
:::

Pentru creditele pe **termen lung**, dobânda neplătită se angajează lunar prin nota contabilă 666 = 1682, iar la plată se stinge datoria prin 1682 = 5121. Pentru creditele pe **termen scurt**, mecanismul e simetric, pe conturile analitice ale grupei 519: angajarea se face 666 = 5198, iar plata 5198 = 5121.

Cele două conturi de dobândă (1682 pentru termen lung, 5198 pentru termen scurt) sunt conturi de pasiv care rețin, între angajare și plată, dobânda datorată și neîncasată/neplătită — soldul lor reprezintă exact această sumă restantă.

## Ce se greșește în practică

O greșeală frecventă este sărirea peste pasul de angajare și înregistrarea directă a plății dobânzii ca 666 = 5121, fără să existe în prealabil o notă de angajare pe 1682/5198. Procedând astfel, dobânda datorată dar neplătită la finalul unei luni nu mai apare corect ca sold în contabilitate, iar evidența datoriei devine incompletă.

O a doua greșeală este confuzia între contul de dobândă pentru termen lung (1682) și cel pentru termen scurt (5198) — cele două sunt distincte și corespund tipului de credit (`lung` sau `scurt`), nu sunt interschimbabile.

## Ce face iConta.eu

Pentru angajarea lunară a dobânzii, aplicația generează automat nota 666 = 1682 (credit pe termen lung) sau 666 = 5198 (credit pe termen scurt), în funcție de tipul de credit selectat. La plată, nota compusă de plată stinge datoria de dobândă angajată anterior prin 1682 = 5121, respectiv 5198 = 5121, alături, dacă e cazul, de rata de principal și de comisionul bancar, în aceeași notă.

[iConta.eu](/)
