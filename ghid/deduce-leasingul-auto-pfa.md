---
title: "Pot deduce leasingul auto la PFA?"
description: "Regula de deductibilitate a ratelor de leasing auto la calculul venitului net al unei persoane fizice autorizate, cu limitarea de 50% din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Pot deduce leasingul auto la PFA?

Da, dar limitat — și limita depinde de cum e folosită mașina, nu de simplul fapt că a fost achiziționată prin leasing.

## Temeiul legal

::: ghid-temei
„(5) Următoarele cheltuieli sunt deductibile limitat: [...]
o) cheltuielile efectuate de utilizator, reprezentând chiria - rata de leasing - în cazul contractelor de leasing operațional, respectiv cheltuielile cu amortizarea și dobânzile pentru contractele de leasing financiar, stabilite în conformitate cu prevederile privind operațiunile de leasing și societățile de leasing;
[...]
(7) Nu sunt cheltuieli deductibile: [...]
k) 50% din cheltuielile aferente vehiculelor rutiere motorizate care nu sunt utilizate exclusiv în scopul desfășurării activității și a căror masă totală maximă autorizată nu depășește 3.500 kg și nu au mai mult de 9 scaune de pasageri, incluzând și scaunul șoferului, aflate în proprietate sau în folosință. Aceste cheltuieli sunt integral deductibile pentru situațiile în care vehiculele respective se înscriu în oricare dintre următoarele categorii: 1. vehiculele utilizate exclusiv pentru servicii de urgență, servicii de pază și protecție și servicii de curierat; 2. vehiculele utilizate de agenții de vânzări și de achiziții; 3. vehiculele utilizate pentru transportul de persoane cu plată, inclusiv pentru serviciile de taximetrie; 4. vehiculele utilizate pentru prestarea de servicii cu plată, inclusiv pentru închirierea către alte persoane sau pentru instruire de către școlile de șoferi; 5. vehiculele utilizate ca mărfuri în scop comercial."
— Legea 227/2015 (Codul fiscal), art. 68 alin. (5) lit. o), alin. (7) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum se combină cele două reguli, în practică:

- **Rata de leasing e, în principiu, cheltuială deductibilă** — chiria pentru leasing operațional, respectiv amortizarea și dobânzile pentru leasing financiar (art. 68 alin. 5 lit. o).
- **Dar 50% din costul asociat mașinii rămâne nedeductibil**, dacă vehiculul nu e folosit exclusiv în scopul activității (art. 68 alin. 7 lit. k) — regula se aplică vehiculelor sub 3.500 kg, cu maximum 9 locuri.
- **Excepția care permite deducerea integrală (100%)**: dacă vehiculul se încadrează într-una din cele 5 categorii de la lit. k) — servicii de urgență, pază, curierat; agenți de vânzări/achiziții; transport de persoane cu plată (taxi); prestări de servicii cu plată/închiriere/școli de șoferi; vehicule folosite ca marfă. Un PFA care folosește mașina și pentru deplasări personale, în afara acestor categorii, rămâne cu limita de 50%.
- Textul de la lit. k) precizează explicit că **amortizarea nu intră** sub incidența acestei limitări — regula de 50% vizează celelalte cheltuieli aferente vehiculului (rata de leasing, combustibil, întreținere), nu amortizarea propriu-zisă.

## Ce se greșește în practică

- Se deduce integral rata de leasing, presupunând că „leasingul e deja o cheltuială de afaceri" — limita de 50% se aplică indiferent de forma de finanțare a mașinii (proprietate, leasing sau închiriere), dacă vehiculul nu e utilizat exclusiv în scop economic.
- Se caută excepția de deducere 100% doar pe baza obiectului de activitate declarat al PFA-ului, fără să se demonstreze efectiv că vehiculul se încadrează concret în una din cele 5 categorii — încadrarea trebuie susținută cu foi de parcurs sau alte documente care arată utilizarea exclusivă.
- Se aplică limita de 50% și la amortizare, deși textul legal o exclude explicit din sfera limitării.

## Ce face iConta.eu

Modulul de leasing din iConta.eu (`core/leasing.py`) generează notele contabile pentru rata de leasing financiar (capital, dobândă, comision) și operațional (chirie), pe baza datelor introduse de contabil. La data acestui ghid, aplicația **nu calculează automat limita de 50% pentru vehicule** de la art. 68 alin. (7) lit. k) și nu verifică încadrarea într-una din cele 5 categorii de deducere integrală — contabilul aplică manual limitarea corespunzătoare la calculul venitului net al PFA-ului, pe baza modului real de utilizare a mașinii.

[iConta.eu](/)
