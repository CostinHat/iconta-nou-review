---
title: "Cum se validează declarația D205?"
description: "Ce înseamnă corectitudinea legală a declarației D205 și ce verificări tehnice trec datele înainte ca declarația să fie considerată validă pentru depunere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se validează declarația D205?

D205 e o declarație informativă privind impozitul reținut la sursă, iar „validarea" ei înseamnă două lucruri diferite, care se confundă des: corectitudinea LEGALĂ a datelor înscrise (o obligație a declarantului, indiferent cine sau ce a completat formularul) și corectitudinea TEHNICĂ a fișierului transmis (structura XML acceptată de ANAF). Fără ambele, declarația fie e respinsă la depunere, fie e acceptată dar greșită.

## Temeiul legal

::: ghid-temei
„(3) Contribuabilul/Plătitorul are obligația de a completa declarația fiscală înscriind corect, complet și cu bună-credință informațiile prevăzute de formular, corespunzătoare situației sale fiscale. Declarația fiscală se semnează de către contribuabil/plătitor sau, după caz, reprezentantul legal ori împuternicitul acestuia."
— Legea 207/2015 (Codul de procedură fiscală), art. 102 alin. (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Răspunderea pentru corectitudinea datelor din D205 (CNP-uri, cote, sume distribuite/plătite) e a plătitorului de dividende, nu a instrumentului folosit pentru generare — indiferent dacă declarația se completează manual sau se generează automat dintr-un program.
- Structura tehnică a formularului D205 (câmpuri obligatorii, valori admise, reguli de unicitate) e stabilită prin OPANAF 179/2022, modificat succesiv de OPANAF 102/2025 și OPANAF 303/2026, iar fișierul XML transmis trebuie să respecte exact această structură.
- ANAF verifică fișierul depus printr-un validator tehnic oficial (validatorul DUK), care respinge declarații cu erori de structură sau de conținut, indiferent dacă sumele din spate sunt corecte fiscal.

## Ce se greșește în practică

- Se trimite declarația fără o verificare prealabilă a structurii, iar erorile de format ies abia la depunerea efectivă pe portalul ANAF/SPV.
- Se introduc CNP-uri de beneficiari fără verificarea cifrei de control, iar respingerea apare abia la validare, nu la momentul introducerii datelor.
- Se presupune că un beneficiar nerezident poate figura pe D205 la fel ca unul rezident — dividendele către nerezidenți nu se declară pe acest formular, ci pe D207.
- Se ignoră faptul că același beneficiar (CNP) nu poate apărea de două ori cu același tip de venit — validatorul respinge duplicatele.

## Ce face iConta.eu

iConta.eu nu are un ecran separat de „completare" a D205 — declarația se generează automat din contul 457 (dividende distribuite/plătite) și din cotele asociaților, iar generatorul aplică, înainte de a produce XML-ul, mai multe verificări reale, confirmate în cod:

- CUI-ul plătitorului și CNP-ul fiecărui beneficiar sunt verificate pe cifra de control (algoritmul oficial de checksum), nu doar pe „necompletat".
- Rezidența beneficiarului se derivă automat din CNP (prima cifră 1-8 = rezident); un beneficiar fără CNP românesc valid e respins la generare, cu mențiunea că trebuie declarat pe D207, nu pe D205.
- Un CNP duplicat pe combinația tip de venit + CNP e blocat explicit înainte de generare, ca să nu ajungă la respingere abia la depunere.
- Un modul separat de reconciliere recalculează independent, din propriile interogări SQL, baza și impozitul per beneficiar din contul 457 și compară rezultatul cu ce a produs generatorul; orice divergență blochează generarea declarației. Pentru beneficiarii introduși manual (nu preluați automat din 457), reconcilierea completă nu se aplică — se verifică doar consistența internă (impozitul calculat = cota × baza).
- Regulile de generare sunt verificate, la nivel de dezvoltare, față de validatorul oficial DUK al ANAF, astfel încât fișierul XML produs să respecte structura acceptată la depunere.

Corectitudinea de fond a datelor sursă — cotele asociaților, sumele înregistrate pe contul 457 — rămâne responsabilitatea contabilului care le introduce; aplicația nu poate valida ce nu poate verifica din exterior.

[iConta.eu](/)
