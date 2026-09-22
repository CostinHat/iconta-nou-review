---
title: Ce se întâmplă dacă nu înregistrez sponsorizarea ca atare?
description: Dacă o cheltuială de sponsorizare este înregistrată contabil ca protocol, donație generică sau altă cheltuială, riscați să nu mai puteți justifica și urmări suma eligibilă pentru creditul fiscal de la impozitul pe profit sau micro, deoarece regimul de deductibilitate e diferit de la o categorie la alta.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce se întâmplă dacă nu înregistrez sponsorizarea ca atare?

O greșeală frecventă este înregistrarea unei sponsorizări sub o altă categorie de cheltuială — protocol, donație generică sau chiar cheltuială de marketing — fără să fie identificată distinct ca sponsorizare. Consecința nu e doar una de ordine contabilă: fără o evidență clară, riscați să pierdeți dreptul la creditul fiscal la care ar fi avut, de fapt, acces firma.

## Temeiul legal

::: ghid-temei
„6582 Donații acordate”

— *Plan de conturi general, OMFP 1802/2014.*

„Contractul de sponsorizare se încheie în forma scrisă, cu specificarea obiectului, valorii și duratei sponsorizării, precum și a drepturilor și obligațiilor părților.”

— *Legea nr. 32/1994 privind sponsorizarea, art. 1 alin. (2).*

„scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele: 1. valoarea calculată prin aplicarea a 0,75% la cifra de afaceri...; 2. valoarea reprezentând 20% din impozitul pe profit datorat. În cazul sponsorizărilor efectuate către entități persoane juridice fără scop lucrativ, inclusiv unități de cult, sumele aferente acestora se scad din impozitul pe profit datorat, în limitele prevăzute de prezenta literă, doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților/unităților de cult pentru care se acordă deduceri fiscale, potrivit alin. (4^1).”

— *Codul fiscal, art. 25 alin. (4) lit. i).*
:::

## De ce contează evidența distinctă

Sponsorizarea are un regim fiscal special — un credit direct din impozitul pe profit (sau, până în 2023, din impozitul micro), calculat pe baza unui plafon legal — complet diferit de regimul cheltuielilor de protocol (care au propriul plafon, distinct, de deductibilitate) sau de cel al altor donații fără bază legală în Legea nr. 32/1994 (care, ca regulă generală, sunt nedeductibile fiscal). Dacă suma nu e izolată contabil, la calculul impozitului nu mai puteți demonstra clar:

- cât ați sponsorizat efectiv, pentru a-l compara cu plafonul legal;
- că sponsorizarea are la bază un contract scris, așa cum cere Legea 32/1994;
- că suma respectă condițiile de eligibilitate a beneficiarului (inclusiv, dacă e cazul, înscrierea în Registrul entităților/unităților de cult).

În plus, fără contract scris, riscați ca organul fiscal să conteste însăși calificarea cheltuielii drept sponsorizare — indiferent cum ați înregistrat-o contabil.

## Ce se greșește în practică

- Sponsorizarea este înregistrată direct pe cheltuieli de protocol, care au un regim de deductibilitate diferit și un plafon separat.
- Nu există un contract scris de sponsorizare, deși Legea nr. 32/1994 art. 1 alin. (2) îl cere explicit — fără el, calificarea cheltuielii poate fi contestată.
- Suma e înregistrată generic, drept „donație”, fără să fie urmărită distinct, ceea ce face imposibilă compararea cu plafonul legal la calculul impozitului.
- Nu se verifică, la data încheierii contractului, dacă beneficiarul e înscris în Registrul entităților/unităților de cult — condiție fără de care întregul credit e nedatorat.
- Se confundă sponsorizarea cu mecenatul sau cu bursele private, care au reguli parțial diferite, deși toate se regăsesc, formal, sub aceeași literă a Codului fiscal.

## Ce face iConta.eu

Funcția `nota_sponsorizare(suma, mod)` din `core/sponsorizari.py` generează automat nota contabilă specifică sponsorizării, izolând-o de alte cheltuieli: `6582 = 401` pentru sponsorizarea acordată prin contract (obligație către beneficiar), respectiv `6582 = 5121` pentru plata directă. Contul 6582 poartă oficial denumirea „Donații acordate” în planul de conturi (nu există un cont dedicat „sponsorizare” în planul de conturi general) — dar folosirea lui distinctă, prin această funcție, vă permite să urmăriți separat sumele eligibile pentru creditul fiscal.

Atenție: funcția acceptă doar modurile `"contract"` și `"plata"` — sponsorizarea în natură (predare de bunuri) nu are, deocamdată, un mod dedicat în motor, deși este menționată în documentația internă a modulului; pentru acest caz, nota contabilă trebuie tratată manual.

[iConta.eu](/)
