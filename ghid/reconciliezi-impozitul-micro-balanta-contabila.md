---
title: "Cum reconciliezi impozitul micro cu balanța contabilă?"
description: "Cum se verifică baza de calcul a impozitului pe veniturile microîntreprinderilor față de rulajele conturilor de venituri din balanță, conform art. 53 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum reconciliezi impozitul micro cu balanța contabilă?

Impozitul pe veniturile microîntreprinderilor se calculează pe bază trimestrială, dintr-o formulă simplă în aparență — venituri totale înmulțite cu cota — dar greșelile apar aproape mereu la un singur pas: ce anume intră în „veniturile totale" declarate și ce anume arată, de fapt, rulajul creditor al conturilor de venituri din balanță. Reconcilierea înseamnă exact această confruntare, linie cu linie.

## Temeiul legal

::: ghid-temei
„Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile aferente costurilor serviciilor în curs de execuție; c) veniturile din producția de imobilizări corporale și necorporale; d) veniturile din subvenții; e) veniturile din provizioane, ajustări pentru depreciere sau pentru pierdere de valoare, care au fost cheltuieli nedeductibile la calculul profitului impozabil sau au fost constituite în perioada în care persoana juridică română era supusă impozitului pe veniturile microîntreprinderilor."
— Codul fiscal (Legea 227/2015), art. 53 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Practic, reconcilierea pornește de la rulajul creditor al conturilor de venituri (clasa 7) din balanța de verificare pe trimestrul respectiv și îl ajustează astfel:

- se **scad** veniturile enumerate la art. 53 alin. (1) lit. a)-e) — printre altele, veniturile din producția de imobilizări, din subvenții și din anumite provizioane/ajustări reluate — pentru că acestea nu intră în baza impozabilă micro, deși apar în rulajul contabil de venituri;
- rezultatul trebuie să corespundă exact cu baza declarată în D100 pentru trimestrul verificat;
- orice diferență nereconciliată e fie o eroare de înregistrare contabilă (o notă validată greșit, o dublare), fie o omisiune a uneia dintre excepțiile legale de mai sus.

## Ce se greșește în practică

- Se ia direct rulajul contului 704 (sau al altui cont de venituri) fără să se verifice dacă în balanță au fost incluse și conturile 758/766/76x (venituri din alte surse, financiare), care intră și ele „din orice sursă" în baza impozabilă potrivit art. 53.
- Se omite scăderea veniturilor din producția de imobilizări corporale/necorporale (art. 53 alin. (1) lit. c)) atunci când firma și-a construit sau dezvoltat intern un activ — o eroare frecventă la firmele care capitalizează cheltuieli de dezvoltare software.
- Se reconciliază baza cu totalul veniturilor din contul de profit și pierdere raportat anual, în loc de rulajul trimestrial efectiv validat în contabilitate — cele două cifre diferă ori de câte ori există note nevalidate sau corecții ulterioare.

## Ce face iConta.eu

iConta.eu are un modul dedicat de reconciliere (motorul din spatele declarației D100), care recalculează **independent** baza impozabilă direct din liniile de contabilitate validate — suma rulajului creditor al conturilor de venituri (70x, 75x, 76x) din care se scade contul 709, pe fereastra calendaristică a trimestrului — și confruntă rezultatul cu ce a fost generat în declarație. Recalcularea nu reia codul generatorului D100, ci recalculează separat, tocmai ca să prindă o eventuală eroare de generare, nu doar s-o repete. Excepțiile de la art. 53 alin. (1) lit. a)-e) (producție de imobilizări, subvenții, anumite provizioane) rămân, la acest moment, ajustări pe care contabilul le verifică și le introduce manual, pentru că depind de natura fiecărei operațiuni și nu pot fi deduse automat doar din simbolul de cont.

[iConta.eu](/)
