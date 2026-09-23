---
title: Cum depun D390 rectificativă?
description: Norma cere un formular nou, cu căsuța de rectificare bifată; la data acestui ghid, generarea automată a acelei căsuțe nu e implementată în iConta.eu — spunem asta direct, nu o ascundem.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum depun D390 rectificativă?

Trebuie spus clar de la început: procedura oficială de rectificare presupune o declarație nouă, cu o căsuță specifică bifată pe formular — iar la data acestui ghid, generarea acelei căsuțe nu e automatizată în iConta.eu. Explicăm mai jos ce prevede norma și cum stau lucrurile în aplicație.

## Temeiul legal

::: ghid-temei
"Declarația depusă inițial se rectifică prin depunerea unei noi declarații, pe același format, bifând căsuța corespunzătoare de pe formular. În declarația rectificativă se rectifică tranzacții declarate în orice perioadă de raportare anterioară și se completează toate rubricile formularului cu datele valabile la momentul declarării, indiferent dacă acestea au mai fost declarate.
ATENȚIE: Informațiile completate eronat în perioade de raportare anterioare nu se corectează prin înscrierea cifrei "0" la rubrica «Bază impozabilă»... Se completează câte o declarație rectificativă pentru fiecare perioadă de raportare pentru care se operează rectificări." — OPANAF nr. 705/2020, Anexa 2, Secțiunea I
:::

Practic, corectarea unei D390 deja depuse înseamnă: o declarație complet nouă, pentru perioada respectivă, cu toate rubricile completate cu valorile corecte (nu doar diferența), și cu bifa de rectificativă activă pe formularul transmis către ANAF. O eroare nu se "șterge" prin trecerea bazei pe zero — se înlocuiește cu valoarea corectă.

## Ce se greșește în practică

- Se încearcă corectarea unei erori din D390 anterioară prin trecerea unei linii pe "0" în declarația curentă — norma interzice explicit acest lucru.
- Se presupune că o simplă redepunere a fișierului XML, fără bifa de rectificativă, e suficientă pentru ANAF.
- Se amestecă operațiuni din perioada curentă cu corecții din perioade anterioare în aceeași declarație, în loc de câte o declarație rectificativă separată pentru fiecare perioadă corectată.

## Ce face iConta.eu

Onest: la data acestui ghid, generatorul XML al D390 din iConta.eu setează întotdeauna căsuța de declarație inițială, nu are un parametru care să o comute pe "rectificativă". Aplicația păstrează intern un istoric al fiecărei regenerări/depuneri (un număr de depunere crescător), ceea ce vă ajută să urmăriți versiunile, dar nu înlocuiește bifa oficială de rectificativă cerută de instrucțiuni. Pentru o corecție conformă normei de mai sus, verificați cu echipa iConta.eu stadiul exact al acestei funcționalități înainte de a depune, sau tratați rectificarea direct pe portalul ANAF.

[iConta.eu](/)
