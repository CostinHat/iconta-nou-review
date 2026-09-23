---
title: Impozitul pe profit la firmele care nu au angajați 2026
description: Numărul de angajați nu are legătură cu bilanțul anual (F013) — ține de impozitul pe profit și de declarația D101, unde criteriul „fără angajați" nu are azi o regulă dedicată identificată.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Impozitul pe profit la firmele care nu au angajați 2026

De la început, o precizare de graniță: acest subiect nu are nicio legătură cu bilanțul anual (S1005/S1003). Întrebarea ține de impozitul pe profit și de declarația D101.

## Temeiul legal

::: ghid-temei
D101 este generată din balanță, pe baza profilului firmei și a rulajelor contabile din clasele 6/7, pentru calculul impozitului pe profit; formularul e reglementat prin ordinul care stabilește modelul și conținutul D101 (OPANAF 206/2025), iar impozitul minim pe cifra de afaceri (IMCA) se calculează conform art. 18^1 din Codul fiscal, pentru firmele cu cifra de afaceri de peste 50.000.000 EUR.
:::

Numărul de angajați ai firmei nu apare, în sursele verificate pentru acest subiect, ca un criteriu al calculului impozitului pe profit propriu-zis sau al IMCA — obligația de plată a impozitului pe profit ține de forma de organizare și de regimul fiscal ales (profit vs. microîntreprindere), nu de faptul că firma are sau nu personal angajat.

## Ce se greșește în practică

- Se caută explicit, în calculul impozitului pe profit sau al D101, o excepție sau o regulă specială pentru firmele fără angajați — o asemenea regulă nu a fost identificată, nici în lege, nici în aplicație.
- Se confundă acest subiect cu regimul de microîntreprindere, unde condiția de a avea (sau nu) cel puțin un salariat poate influența cota de impozitare — un subiect distinct de impozitul pe profit clasic și de D101.

## Ce face iConta.eu

Trebuie spus deschis unde se termină ce a putut fi verificat: acest subiect nu ține de funcționalitatea de bilanț (F013), ci de **F027 — Declarația D101 + IMCA** (`core/d101.py`). Verificat direct în cod: nu există nicio ramură de calcul legată de numărul de angajați (`grep -n "angajat" core/d101.py` → 0 rezultate) — impozitul pe profit și IMCA se calculează la fel, indiferent dacă firma are sau nu personal angajat. Dacă întrebarea vizează de fapt condiția de a avea cel puțin un salariat pentru cota redusă de impozitare la **microîntreprinderi** (un regim diferit de impozitul pe profit), aceasta nu are azi o funcționalitate dedicată identificată în dosarul de cercetare al acestui ghid — nu putem confirma aici acest aspect.

[iConta.eu](/)
