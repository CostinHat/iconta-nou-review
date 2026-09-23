---
title: "Cum se casează stocurile expirate sau degradate"
description: "De ce stocurile expirate sau degradate constatate la inventariere nu se «casează», ci se scad din gestiune prin operația Minus, și ce TVA se ajustează."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se casează stocurile expirate sau degradate

O precizare de terminologie e importantă înainte de pasul practic: „casarea" este, strict, operația prin care se scoate din evidență un **mijloc fix** uzat sau distrus. Pentru stocuri (mărfuri, materii prime, produse) expirate sau degradate, operația corectă este **scăderea din gestiune ca lipsă neimputabilă**, nu casarea.

## Temeiul legal

::: ghid-temei
"cheltuielile privind bunurile de natura stocurilor sau a mijloacelor fixe amortizabile constatate lipsă din gestiune ori degradate, neimputabile, precum și taxa pe valoarea adăugată aferentă, dacă aceasta este datorată potrivit prevederilor titlului VII. Aceste cheltuieli sunt deductibile în următoarele situații/condiții: [...] 3. bunurile/mijloacele fixe amortizabile degradate calitativ, dacă se face dovada distrugerii; [...] 7. alte bunuri [...] dacă termenul de valabilitate/expirare este depășit, potrivit legii." — Codul fiscal, art. 25 alin. (4) lit. c)
:::

Regula generală este că o cheltuială cu stocuri degradate sau expirate, neimputabile, este **nedeductibilă**; devine deductibilă doar dacă se încadrează la unul din punctele enumerate limitativ de lege — pentru degradare, condiția este dovada distrugerii; pentru expirare, depășirea termenului de valabilitate potrivit legii.

## Ce se greșește în practică

- Se caută în aplicație operația „Casare" pentru un stoc degradat — aceasta este rezervată mijloacelor fixe (scoaterea din registrul de mijloace fixe, cu descărcarea amortizării cumulate).
- Se tratează degradarea/expirarea ca deductibilă automat, fără documentul care dovedește distrugerea efectivă (proces-verbal de distrugere, casare fizică).
- Se omite ajustarea de TVA atunci când distrugerea nu este dovedită corespunzător.

## Ce face iConta.eu

Pentru stocuri, aplicația folosește operația **Minus** din ecranul „Inventariere anuală", pe unul din conturile de stoc acceptate (371, 301, 302, 303, 345 sau 381 — orice alt cont de stoc este refuzat de motorul de calcul). Cota de TVA trebuie introdusă explicit, fără valoare implicită. Dacă lipsa/degradarea este marcată ca asigurată sau dovedit distrusă, nota nu mai include linia de ajustare TVA; altfel, aplicația generează automat ajustarea 635 = 4426. Deductibilitatea la impozitul pe profit rămâne, în toate cazurile, o evaluare pe care o face contabilul pe baza documentelor justificative — aplicația nu decide automat dacă cele 7 condiții din art. 25 alin. (4) lit. c) sunt îndeplinite.

[iConta.eu](/)
