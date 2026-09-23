---
title: "Monografia impozitului pe dividende în 2026"
description: "Notele contabile pentru distribuirea, impozitarea și plata dividendelor în 2026, pentru dividende anuale și interimare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Monografia impozitului pe dividende în 2026

Contabilizarea dividendelor presupune trei momente distincte: aprobarea/distribuirea, reținerea impozitului și plata efectivă către asociați — fiecare cu propria notă contabilă.

## Temeiul legal

::: ghid-temei
"(7) Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...] către acționari/asociați/investitori."
— Codul fiscal, art. 97 alin. (7), formă în vigoare de la distribuirile din 2026 (`anaf_surse/cod_fiscal_227_2015_consolidat.txt:9470-9474`), modificată de Legea 141/2025 art. II pct. 5
:::

Pentru dividende **anuale** (aprobate pe baza situațiilor financiare anuale), fluxul de note contabile documentat în aplicație este: 1171 → 457 (distribuire din profit), 457 → 446 (reținere impozit), 457 → 5121 (plată efectivă către asociat).

Pentru dividende **interimare** (distribuite în cursul anului, pe baza situațiilor financiare interimare), fluxul este: 463 → 456, impozit 456 → 446, plată 456 → 5121, urmat de regularizare după aprobarea situațiilor financiare anuale — inclusiv restituirea unui eventual exces prin nota 5121 = 456, dacă dividendul interimar aprobat ulterior este mai mic decât cel plătit.

Cota aplicabilă pentru dividendele distribuite începând cu 1 ianuarie 2026 este **16%** (Legea 141/2025 art. II pct. 5 → CF art. 97 alin. 7); pentru dividendele distribuite pe baza situațiilor financiare interimare din 2025, cota rămâne 10%, fără recalculare ulterioară (Legea 141/2025 art. VII alin. 2).

## Ce se greșește în practică

Cele mai frecvente greșeli sunt: aplicarea cotei de la data plății în loc de cota de la data distribuirii, tratarea dividendelor interimare fără regularizare ulterioară la aprobarea bilanțului anual, și omiterea notei de restituire a excesului atunci când situațiile financiare anuale aprobă un dividend mai mic decât cel plătit interimar.

## Ce face iConta.eu

Motorul de generare a notelor contabile pentru decontări cu asociații (`core/decontari_asociati.py`) generează automat notele descrise mai sus, pentru fluxul anual și pentru cel interimar, inclusiv regularizarea și restituirea de exces. Acest modul nu face parte din funcționalitatea D205 propriu-zisă, dar alimentează contul 457 din care D205 își preia ulterior baza de calcul. Notă de onestitate: temeiul citat intern pentru aceste note include și OMFP 3067/2018, a cărui text nu a putut fi verificat direct în sursele locale — dacă vă bazați pe acest ghid pentru o dispută punctuală de reglementare contabilă, verificați separat acel ordin.

[iConta.eu](/)
