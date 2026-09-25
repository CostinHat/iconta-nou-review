---
title: "Contabilitatea unei firme de închirieri auto: TVA și TVA la marjă"
description: "Regula deducerii integrale a TVA pentru vehiculele destinate închirierii și situația în care intervine regimul special de marjă la revânzarea mașinilor uzate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unei firme de închirieri auto: TVA și TVA la marjă

O firmă de închirieri auto întâlnește, de regulă, două probleme distincte de TVA: deducerea taxei aferente achiziției/întreținerii flotei (unde regula generală de limitare la 50% nu se aplică) și, separat, tratamentul TVA atunci când vinde mai departe mașinile scoase din flotă — caz în care poate deveni relevant regimul special de marjă. Sunt două subiecte diferite, care se ating, dar nu se suprapun.

## Temeiul legal

::: ghid-temei
„Articolul 298 Limitări speciale ale dreptului de deducere (1) Prin excepție de la prevederile art. 297 se limitează la 50% dreptul de deducere a taxei aferente cumpărării, achiziției intracomunitare, importului, închirierii sau leasingului de vehicule rutiere motorizate și a taxei aferente cheltuielilor legate de vehiculele aflate în proprietatea sau în folosința persoanei impozabile, în cazul în care vehiculele nu sunt utilizate exclusiv în scopul activității economice. [...] (3) Prevederile alin. (1) nu se aplică următoarelor categorii de vehicule rutiere motorizate: [...] e) vehiculele utilizate pentru închiriere sau a căror folosință este transmisă în cadrul unui contract de leasing financiar ori operațional;"
— Codul fiscal (Legea 227/2015), art. 298 alin. (1) și alin. (3) lit. e) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text:

- **Regula generală** (art. 298 alin. (1)) limitează la 50% deducerea TVA pentru vehicule rutiere motorizate care nu sunt folosite exclusiv în scop economic.
- **Excepția de la alin. (3) lit. e)** scoate expres de sub această limitare vehiculele utilizate pentru **închiriere** (sau transmise prin leasing) — pentru o firmă al cărei obiect de activitate e chiar închirierea auto, deducerea TVA e **integrală (100%)**, nu limitată la jumătate, exact fiindcă mașinile sunt destinate acestei activități economice.
- Separat de deducere, dacă firma **vinde ulterior** mașinile uzate scoase din flotă, iar acestea se încadrează în definiția „bunurilor second-hand" din art. 312 CF și au fost achiziționate de la un vânzător fără drept de deducere (persoană neimpozabilă, întreprindere mică etc.), poate opta pentru **regimul special de marjă** — taxare doar pe diferența dintre prețul de vânzare și prețul de cumpărare, nu pe prețul întreg.

## Ce se greșește în practică

- Se aplică din reflex limitarea de 50% la deducerea TVA pentru toată flota unei firme de închirieri, fără să se verifice excepția explicită de la art. 298 alin. (3) lit. e).
- Se presupune că, fiindcă firma face „TVA la marjă" pe unele vânzări de mașini uzate, regimul de marjă se aplică automat și veniturilor din chirii — cele două operațiuni (chiria propriu-zisă și revânzarea unei mașini scoase din flotă) au regimuri de TVA complet diferite.
- Se omite verificarea condiției de fond a regimului de marjă la revânzare: nu orice mașină uzată vândută de o firmă de închirieri califică automat — depinde de la cine a fost cumpărată inițial mașina și dacă acel vânzător a aplicat sau nu TVA deductibil.

## Ce face iConta.eu

Subiectul „TVA la marjă" din acest titlu e acoperit doar parțial și tangențial de funcționalitățile iConta.eu legate de regimul special de marjă: motorul de calcul al marjei și raportul „Jurnal regim marjă", care înregistrează și, respectiv, listează exclusiv **vânzările** unei firme în regim de marjă (art. 312 pentru second-hand, art. 311 pentru turism) — util, de exemplu, dacă firma de închirieri vinde mai departe o mașină uzată eligibilă pentru acest regim. Partea de deducere TVA la achiziția/întreținerea flotei (limitarea de 50% și excepțiile de la art. 298, inclusiv cea pentru închiriere) și partea de venituri din chirii **nu au legătură** cu acest circuit — nu s-a identificat, în codul aplicației, un modul dedicat limitării de 50% la deducerea TVA pentru vehicule. Contabilitatea completă a unei firme de închirieri auto rămâne, în cea mai mare parte a ei, în afara acestei funcționalități punctuale.

[iConta.eu](/)
