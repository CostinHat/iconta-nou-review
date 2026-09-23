---
title: "Ajustările pentru creanțe neîncasate sunt deductibile?"
description: "Da, dar limitat: 30% peste 270 de zile de la scadență, sau 100% la faliment declarat/insolvență — și doar dacă creanța nu e garantată și nu e la o persoană afiliată."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ajustările pentru creanțe neîncasate sunt deductibile?

Ajustările pentru deprecierea creanțelor sunt deductibile, dar niciodată integral și niciodată necondiționat — Codul fiscal prevede două praguri de deducere, fiecare cu propriile condiții cumulative, iar o creanță garantată sau la o persoană afiliată nu e deductibilă deloc, indiferent de vechime sau de starea debitorului.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] c) ajustările pentru deprecierea creanțelor [...] în limita unui procent de 30% din valoarea acestor ajustări [...] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței; 2. nu sunt garantate de altă persoană; 3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului."

*(Codul fiscal — Legea nr. 227/2015, art. 26 alin. (1) lit. c))*
:::

## Cele două praguri de deducere

1. **30% (art. 26 alin. (1) lit. c))** — creanța e neîncasată de peste 270 de zile de la scadență, negarantată, la un client neafiliat.
2. **100% (art. 26 alin. (1) lit. j))** — debitorul are declarată procedura de faliment prin hotărâre judecătorească, sau e persoană fizică în procedură de insolvență, iar creanța rămâne negarantată și neafiliată.

Condițiile de negarantare și neafiliere sunt cumulative cu celelalte, la ambele praguri — o creanță garantată rămâne nedeductibilă chiar dacă debitorul intră în faliment.

## Ce se greșește în practică

- Se presupune deductibilitate integrală (100%) doar pentru simpla depășire a termenului de scadență, fără să se verifice pragul corect (30%, nu 100%, în afara falimentului).
- Se aplică procentul la soldul creanței, nu la valoarea ajustării contabile constituite.
- Se ignoră condiția de negarantare — o creanță garantată printr-o scrisoare de garanție bancară rămâne nedeductibilă, oricât de veche.

## Ce face iConta.eu

Funcția `deductibilitate_creanta(zile_depasire_scadenta, garantata, afiliata, faliment_declarat)` din `core/provizioane.py` calculează procentul deductibil exact în această ordine: creanță garantată sau afiliată → 0%, indiferent de alți parametri; faliment declarat/insolvență PF → 100%; peste 270 de zile (altfel) → 30%; sub 270 de zile → 0%. Aplicația nu preia automat rezultatul în declarația de impozit pe profit — valoarea nedeductibilă se introduce manual la rândurile corespunzătoare.

[iConta.eu](/)
