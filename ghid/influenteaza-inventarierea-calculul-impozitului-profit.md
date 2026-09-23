---
title: "Cum influențează inventarierea calculul impozitului pe profit?"
description: "Cum notele contabile generate de inventarierea anuală ajung să influențeze impozitul pe profit, prin cheltuielile nedeductibile aferente lipsurilor/degradărilor neimputabile — fără ca inventarierea să calculeze ea însăși impozitul."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum influențează inventarierea calculul impozitului pe profit?

Inventarierea anuală nu calculează, ea însăși, impozitul pe profit — dar rezultatele ei (plusuri, lipsuri, casări) generează note contabile care alimentează balanța din care pornește, mai târziu, declarația anuală de impozit pe profit.

## Temeiul legal

::: ghid-temei
"cheltuielile privind bunurile de natura stocurilor sau a mijloacelor fixe amortizabile constatate lipsă din gestiune ori degradate, neimputabile, precum și taxa pe valoarea adăugată aferentă, dacă aceasta este datorată potrivit prevederilor titlului VII. Aceste cheltuieli sunt deductibile în următoarele situații/condiții: [...]" — Codul fiscal, art. 25 alin. (4) lit. c)
:::

Legătura funcționează astfel: cheltuiala cu o lipsă sau degradare **neimputabilă** care nu se încadrează la una din situațiile enumerate limitativ (calamitate, bun asigurat, degradare dovedit distrusă, bunuri expirate ș.a.) este **nedeductibilă** la impozitul pe profit. Această cheltuială nedeductibilă, înregistrată contabil de nota de inventariere, se regăsește ulterior în rândurile de „cheltuieli nedeductibile" din declarația anuală de impozit pe profit, majorând baza impozabilă.

Pentru partea **imputabilă** a unei lipse (recuperată de la o persoană vinovată), regimul e diferit: cheltuiala cu descărcarea de gestiune e compensată de venitul din imputare (7581) — nu cade sub art. 25 alin. (4) lit. c), care vizează explicit lipsurile neimputabile.

## Ce se greșește în practică

- Se așteaptă ca aplicația să calculeze automat, din ecranul de inventariere, impactul asupra impozitului pe profit — inventarierea produce doar notele contabile, nu declarația de impozit.
- Se omite din calculul impozitului pe profit cheltuiala nedeductibilă generată de o lipsă neimputabilă, pentru că „a fost deja înregistrată contabil".
- Se tratează lipsa imputabilă (compensată prin venit din imputare) la fel ca cea neimputabilă (potențial nedeductibilă), deși regimurile fiscale diferă.

## Ce face iConta.eu

Ecranul „Inventariere anuală" (categoria „Imobilizări și capital") produce exclusiv notele contabile aferente plusurilor, lipsurilor și casărilor constatate — nu calculează impozitul pe profit. Regularizarea anuală a impozitului pe profit este o funcționalitate separată, distinctă de ecranul de inventariere, care pornește din balanța rezultată (inclusiv din notele generate aici) pentru a stabili cheltuielile nedeductibile și impozitul datorat.

[iConta.eu](/)
