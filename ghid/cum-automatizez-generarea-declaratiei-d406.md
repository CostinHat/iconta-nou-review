---
title: Cum automatizez generarea declarației D406?
description: Generarea D406 urmează un flux în patru pași — preluare date, asamblare, validare structurală internă și construire XML — dar validarea oficială ANAF (DUKIntegrator) rămâne un pas extern obligatoriu, nu este înlocuită de validarea din aplicație.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum automatizez generarea declarației D406?

Generarea manuală a fișierului SAF-T, secțiune cu secțiune, este impracticabilă pentru un contabil care gestionează mai multe firme — de aceea D406 este una dintre declarațiile pentru care automatizarea contează cel mai mult. Este util de știut totuși care parte a procesului e cu adevărat automată și unde rămâne un pas manual, extern, obligatoriu.

## Temeiul legal

::: ghid-temei
"1. Declaraţia informativă D406 se transmite în format electronic, data-limită de
transmitere fiind: - ultima zi calendaristică a lunii următoare perioadei de raportare,
respectiv luna/trimestrul calendaristic, după caz, pentru alte informaţii decât cele privind
secţiunile "Stocuri" şi "Active"; - la termenul de depunere a situaţiilor financiare
aferente exerciţiului financiar, în cazul secţiunii "Active"; - la termenul stabilit de
organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data
solicitării, în cazul secţiunii "Stocuri"."
(opanaf_1783_2021_saft_d406.txt, Anexa 4, pct. 1)

"6. În situaţia în care contribuabilul constată anumite erori în declaraţia depusă iniţial,
acesta poate depune declaraţii rectificative."
(opanaf_1783_2021_saft_d406.txt, Anexa 4, pct. 6)
:::

## Fluxul real de generare

Automatizarea D406 înseamnă patru pași înlănțuiți:

1. **Preluarea datelor** din contabilitate: profilul firmei, planul de conturi (deja filtrat pe nomenclatorul normei contabile aplicabile), clienți și furnizori, notele contabile validate din perioada de raportare, facturile de vânzare/cumpărare și plățile.
2. **Asamblarea** structurii declarației, inclusiv generarea automată a avertismentelor (de exemplu metode de plată necunoscute, înlocuite tacit cu un cod implicit, dar semnalate explicit contabilului).
3. **Validarea structurală proprie**: se verifică prezența CUI-ului și numelui firmei, un plan de conturi nevid, unicitatea identificatorului de cont, tipuri de cont valide, echilibrul debit=credit pe fiecare notă contabilă, și coerența TVA pe fiecare linie de factură (suma brută trebuie să fie egală cu net + TVA, cu o toleranță de 0,02 lei).
4. **Construirea fișierului XML** final, în formatul `AuditFile` cerut de ANAF.

::: ghid-exemplu
Dacă o notă contabilă are un dezechilibru de 0,05 lei între debit și credit, pasul de validare structurală îl semnalează înainte ca fișierul XML să fie generat — evitând o respingere ulterioară la validarea oficială, unde diagnosticul ar fi mai greu de interpretat.
:::

## Ce se greșește în practică

- Se consideră că un XML generat fără erori în aplicație este automat "valid pentru ANAF" — validarea structurală internă este doar un prim filtru, nu validarea oficială.
- Se omite rularea validatorului oficial ANAF (DUKIntegrator) înainte de depunere, deși acesta rămâne pasul final obligatoriu.
- Se presupune că datele de clienți/furnizori se populează automat din facturile emise direct în modul respectiv, deși facturile create direct nu alimentează automat nomenclatoarele de clienți/furnizori dacă acestea sunt goale.
- Se ignoră avertismentele afișate la generare (metode de plată necunoscute, cote de TVA nerecunoscute), considerându-le informative, deși semnalează date care pot bloca validarea oficială.
- Se depune o declarație rectificată parțial, corectând doar câmpurile greșite, în loc de a retransmite integral fișierul corectat.

## Ce face iConta.eu

Fluxul de generare este automatizat prin patru funcții înlănțuite din motorul D406: `pull()` citește datele din baza de date (profil firmă, plan de conturi filtrat, parteneri, note contabile validate din fereastra de raportare, facturi, plăți), `construieste()` asamblează rezultatul și lista de avertismente, `valideaza()` rulează verificările structurale proprii ale aplicației (echilibru debit/credit, coerență TVA pe linie, CUI/nume prezente, unicitate AccountID), iar `build_xml()` produce fișierul final. Mesajul afișat la fiecare generare reamintește explicit pasul următor, obligatoriu: validarea finală cu instrumentul oficial ANAF, `DUKIntegrator_AnLunaUI.jar`, instalat pe server — validarea internă din aplicație nu îl înlocuiește.

[iConta.eu](/)
