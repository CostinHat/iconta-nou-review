---
title: "Cum se depune D406 rectificativă?"
description: Ce înseamnă o declarație D406 rectificativă potrivit OPANAF 1783/2021 — cum devine automat rectificativă a doua depunere pentru aceeași perioadă și când se aplică excepțiile de la sancțiune din Codul de procedură fiscală.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se depune D406 rectificativă?

D406 nu are un formular separat de „rectificativă" pe care contribuabilul trebuie să-l bifeze. Statutul declarației rezultă automat din ordinea depunerilor pentru aceeași perioadă.

## Temeiul legal

::: ghid-temei
„Prima Declaraţie informativă D406 validată, depusă pentru o lună sau un trimestru de către un contribuabil/plătitor este considerată declaraţie iniţială. Declaraţiile ulterioare depuse pentru aceeaşi perioadă (lună/trimestru) sunt automat considerate declaraţii rectificative." — OPANAF nr. 1783/2021, Anexa 3, pct. 18.
:::

## Cum funcționează, în practică

A doua (sau a treia) D406 validă, depusă pentru aceeași lună sau același trimestru, devine automat rectificativă — nu există un cod sau o bifă separată de setat manual la depunere. Procedura de generare rămâne aceeași ca la prima depunere: generare XML, validare cu instrumentul oficial denumit în ordin „Validator" (Soft J), generare PDF cu XML-ul atașat și semnat electronic, apoi transmitere prin SPV sau prin e-guvernare.ro (Anexa 3, pct. 1-9).

Legea prevede și o zonă de toleranță pentru corectarea erorilor. Codul de procedură fiscală stabilește sancțiunile pentru nedepunere sau depunere incorectă:

> „(1) Constituie contravenţii următoarele fapte: a) nedepunerea la termenele prevăzute de lege a fişierului standard de control fiscal; b) depunerea incorectă ori incompletă a fişierului standard de control fiscal. (2) Contravenţiile ... se sancţionează astfel: a) cu amendă de la 1.000 lei la 5.000 lei în cazul săvârşirii faptei prevăzute la lit. a); b) cu amendă de la 500 lei la 1.500 lei în cazul săvârşirii faptei prevăzute la lit. b)." — Legea nr. 207/2015 (Codul de procedură fiscală), art. 337^1, alin. (1)-(2)

Alineatul (3) al aceluiași articol prevede excepții de la sancțiune atunci când corectarea se face până la termenul următoarei depuneri, sau ca urmare a unui fapt neimputabil contribuabilului — exact situația unei rectificative depuse din proprie inițiativă, la scurt timp după declarația inițială.

## Ce se greșește în practică

- Se așteaptă un formular sau o secțiune distinctă „D406 rectificativă" — nu există; statutul de rectificativă rezultă automat din ordinea depunerilor pentru aceeași perioadă.
- Se presupune că orice rectificativă atrage automat amendă — legea prevede explicit excepții pentru corectarea la timp sau din motive neimputabile.
- Se confundă rectificativa D406 cu rectificativa altor declarații (D300, D100) — fiecare are propriul regim, chiar dacă terminologia „rectificativ" e comună.

## Ce face iConta.eu

iConta.eu generează și validează fiecare depunere D406 în același flux, indiferent dacă e prima sau o rectificativă pentru aceeași perioadă — fișierul e trecut prin DUKIntegrator, validatorul structural folosit și de ANAF, înainte de a fi pus la dispoziție pentru transmitere. Statutul de declarație inițială sau rectificativă se stabilește de ANAF la depunere, pe baza istoricului declarațiilor deja validate pentru acea perioadă — nu e o setare din aplicație.

[iConta.eu](/)
