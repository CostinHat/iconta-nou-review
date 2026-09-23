---
title: "Ce fac dacă am declarat TVA greșit în D300?"
description: O greșeală în D300 nu se remediază printr-o rectificativă clasică — se corectează prin decontul unei perioade ulterioare, la rândurile de regularizări, cu excepția erorilor pur materiale, care au o procedură separată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am declarat TVA greșit în D300?

Prima reacție, la o greșeală în decontul de TVA, e de obicei „depun o rectificativă". Pentru TVA, legea prevede altceva: corecția trece printr-un decont ulterior, nu printr-o declarație care înlocuiește decontul greșit.

## Temeiul legal

::: ghid-temei
**Art. 323 alin. (3) Cod fiscal (Legea 227/2015):** *„Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare şi se vor înscrie la rândurile de regularizări."*

**Art. 105 Cod de procedură fiscală (Legea 207/2015):**
- alin. (1): *„Declaraţia de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripţie a dreptului de a stabili creanţe fiscale."*
- alin. (4): *„... în cazul taxei pe valoarea adăugată, corectarea erorilor din deconturile de taxă se realizează potrivit prevederilor Codului fiscal [art. 323 alin. (3)]. Erorile materiale din decontul de TVA se corectează potrivit procedurii aprobate prin ordin al preşedintelui A.N.A.F."*
- alin. (5): *„Declaraţia de impunere nu poate fi depusă şi nu poate fi corectată după anularea rezervei verificării ulterioare"*, cu excepțiile de la alin. (6).
:::

## Ce faci, în funcție de tipul greșelii

- **Greșeală de fond** (sumă greșită de TVA colectată sau dedusă, cotă greșită, operațiune omisă) — se corectează prin **decontul unei perioade fiscale ulterioare**, la rândurile de regularizări. Nu se depune o rectificativă separată pentru perioada greșită.
- **Eroare materială** (fără impact asupra cuantumului taxei — de exemplu o greșeală de formă) — se corectează printr-o procedură separată, aprobată prin ordin ANAF, nu prin rândurile de regularizări.
- **Termenul limită** pentru orice corecție e legat de prescripția dreptului organului fiscal de a stabili creanțe fiscale — 5 ani de la 1 iulie a anului următor celui pentru care se datorează obligația (art. 110 Cod de procedură fiscală).
- **Excepție care blochează corecția** — după anularea rezervei verificării ulterioare (de regulă, în urma unei inspecții fiscale finalizate), declarația nu mai poate fi corectată, cu excepțiile prevăzute la art. 105 alin. (6) (condiție legală ulterioară, hotărâre judecătorească definitivă).

## Ce se greșește în practică

- **Se depune o „declarație rectificativă D300"**, ca la alte tipuri de declarații, în loc să se folosească mecanismul specific de regularizare în decontul unei perioade ulterioare.
- **Se așteaptă un decont viitor „potrivit" pentru corecție**, deși legea nu cere o anumită perioadă — corecția se face în decontul perioadei în care se descoperă eroarea.
- **Se încearcă o corecție după anularea rezervei verificării ulterioare**, fără să se verifice dacă situația se încadrează la una din excepțiile de la art. 105 alin. (6).

## Ce face iConta.eu

Panoul manual dedicat regularizărilor TVA (`core/d300_manual_api.py`) permite introducerea corecțiilor direct în decontul curent, cu recalculare automată la fiecare modificare. Aplicația nu automatizează încadrarea greșelii (regularizare de fond vs. eroare materială) și nu verifică dacă rezerva verificării ulterioare a fost anulată pentru perioada respectivă — aceste decizii rămân ale contabilului.

[iConta.eu](/)
