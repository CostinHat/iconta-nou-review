---
title: "Beneficii ale SAF-T pentru controlul intern al firmei"
description: "Ce este fișierul standard de control fiscal (SAF-T/D406) și cum ajută, dincolo de obligația declarativă, la controlul intern al datelor contabile."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Beneficii ale SAF-T pentru controlul intern al firmei

SAF-T (Standard Audit File for Tax), depus în România ca declarația informativă D406, a fost introdus ca instrument de control fiscal pentru ANAF, dar structura lui standardizată — care obligă la o corespondență strictă între jurnalele contabile, documentele sursă și partenerii — are un efect secundar util și pentru firmă: expune inconsistențe din propria evidență contabilă înainte ca acestea să ajungă vizibile într-un control.

## Temeiul legal

::: ghid-temei
„Fișierul standard de control fiscal (SAF-T) se transmite de către contribuabili/plătitori prin intermediul Declarației informative privind fișierul standard de control fiscal, denumită în continuare Declarația informativă D406 [...] SAF-T permite organelor fiscale accesul la date din evidența contabilă și fiscală [...] SAF-T este un fișier în format electronic, de tip XML, conținând date extrase automat din sistemele informatice ale contribuabililor/plătitorilor, exportate și stocate într-un format standardizat."
— OPANAF 1783/2021, art. 2 și anexa 1, pct. 2-3 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

De ce structura SAF-T ajută la controlul intern, nu doar la raportarea către ANAF:

- **Fiecare tranzacție trebuie legată de un partener identificat** (cod, CUI) — o factură fără partener corect asociat sau cu CUI invalid iese la iveală la generarea D406, nu la un control ulterior.
- **Jurnalele de origine trebuie să corespundă exact soldurilor din balanța contabilă** — orice diferență între ce arată registrele și ce arată balanța devine vizibilă la validarea fișierului, înainte de depunere.
- **Secțiunea de active (mijloace fixe)** cere ca fiecare activ amortizabil să aibă o mișcare de amortizare coerentă lună de lună — o lună „uitată" la calculul amortizării se vede direct în structura fișierului.
- **Secțiunea de mișcări de stocuri** obligă la o corelare consecventă între NIR-uri, facturi și ieșiri din gestiune — util tocmai pentru a depista stocurile negative sau discrepanțele de cost descrise în alte ghiduri.
- Chiar și pentru firmele care nu au încă obligația de depunere, structura SAF-T poate fi folosită ca un „audit intern" al calității datelor din contabilitate.

## Ce se greșește în practică

- SAF-T e privit exclusiv ca o obligație declarativă suplimentară, generată mecanic la termen, fără să se folosească erorile de validare ca semnal pentru corectarea datelor din contabilitatea curentă.
- Se ignoră erorile de validare aparent minore (partener neconform, cod de cont nemapat) pentru că declarația „a trecut" oricum, deși aceleași erori afectează și rapoartele interne generate din aceleași date.
- Nu se verifică periodic corelarea dintre jurnale și balanță în afara perioadei de depunere a D406, deși discrepanțele se acumulează lună de lună dacă nu sunt corectate la sursă.

## Ce face iConta.eu

iConta.eu generează declarația D406/SAF-T (`core/d406.py`, `core/d406_active.py`, `core/d406_stocuri.py`) pe baza acelorași date de contabilitate, mijloace fixe și stocuri folosite și pentru celelalte declarații și rapoarte din aplicație, cu validare pe structura oficială ANAF (XSD-ul publicat) înainte de generare. Faptul că fișierul D406 se construiește din exact aceleași înregistrări pe care contabilul le vede zilnic în aplicație înseamnă că o eroare de corelare (partener, sold, amortizare) devine vizibilă la generarea declarației, nu doar la un eventual control ANAF — acesta e beneficiul concret pentru controlul intern, oferit ca efect al modului în care aplicația ține evidența contabilă generală.

[iConta.eu](/)
