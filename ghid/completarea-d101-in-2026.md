---
title: Cum se completează D101 în 2026?
description: D101 pe 2026 se completează pe schema OPANAF 206/2025 (v10), cu cota standard de 16% (art. 17), cota de 5% pentru baruri/cluburi de noapte (art. 18), și impozitul minim pe cifra de afaceri calculat pentru firmele peste 50.000.000 euro cu cota redusă la 0,5%, nu 1% (art. 18^1 alin. 16 Cod fiscal).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se completează D101, declarația anuală de impozit pe profit, în 2026?

D101 pe 2026 se depune pe schema aprobată prin OPANAF 206/2025, care aduce în formular și noutatea cea mai importantă a anului: cota redusă a impozitului minim pe cifra de afaceri, de la 1% la 0,5%. Restul structurii formularului — de la rezultatul contabil la profitul impozabil, apoi la impozitul final — rămâne cea consacrată, dar fiecare rând are condiții exacte de completare, iar omiterea uneia schimbă suma finală.

## Temeiul legal

::: ghid-temei
**OPANAF 206/2025** — actul normativ pe baza căruia se completează formularul: *„ORDIN Nr. 206 din 11 februarie 2025 pentru aprobarea modelului, conținutului și instrucțiunilor de completare a formularelor 101 «Declarație privind impozitul pe profit» și 101 Grup fiscal..."*

**CF art. 17** — cota standard: *„Cota de impozitare. Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."*

**CF art. 18** — cota specială pentru un sector distinct: *„Contribuabilii care desfăşoară activităţi de natura barurilor de noapte, cluburilor de noapte, discotecilor sau cazinourilor ... sunt obligaţi la plata impozitului în cotă de 5% aplicat acestor venituri înregistrate."*

**CF art. 18^1 alin. (16), adăugat de OUG 89/2025 art. I pct. 1, publicat în MO 1203/24.12.2025:** *„Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin. (3) este 0,5%."*

**OPANAF 206/2025, instrucțiuni rd. 39.1:** *„Rândul 391 se completează cu valoarea pierderii fiscale de recuperat în perioada curentă, potrivit art. 31 din Legea nr. 227/2015... Rândul se completează numai în situaţia în care se declară profit (rândul 381)."*
:::

## Structura formularului, în ordine

```
rd.22   rezultatul contabil al anului
rd.34   total cheltuieli nedeductibile (suma rd.23...rd.33)
rd.35   rd.22 + rd.34
rd.38.1 rd.35 + rd.36 + rd.37 - rd.38     (alte ajustări)
rd.39   pierdere fiscală de recuperat din anii precedenți
rd.39.1 pierdere recuperată în anul curent (≤ rd.39, doar dacă rd.38.1 e profit)
rd.40   rd.38.1 - rd.39.1                  (profitul impozabil)
rd.41.1 rd.40 × 16%                        (impozit la cota standard)
```

Pentru firmele cu activitate de baruri de noapte, cluburi de noapte, discoteci sau cazinouri, veniturile din acea activitate se impozitează separat, cu cota de 5% (art. 18), și nu intră în calculul de la rd. 41.1 la cota standard.

## Comparația cu impozitul minim pe cifra de afaceri

Dacă cifra de afaceri a anului precedent, calculată în euro la cursul de la închiderea exercițiului financiar, depășește 50.000.000 euro, completezi și secțiunea de comparație cu IMCA:

```
rd.46 = impozitul pe profit clasic, pregătit pentru comparație
rd.47 = impozitul la nivelul IMCA = cotă × (VT − Vs − I − A)
dacă rd.46 >= rd.47  ->  rd.48.1 (impozitul pe profit clasic)
dacă rd.47 > rd.46    ->  rd.48.2 (IMCA)
```

**Cota din formula IMCA pentru anul fiscal 2026 e 0,5%, nu 1%.** Formula generală din art. 18^1 alin. (3) prevede 1%, dar alin. (16), introdus de OUG 89/2025, o reduce explicit doar pentru anul fiscal 2026 (respectiv anul fiscal modificat care începe în 2026). Aplicarea cotei generale de 1% la o declarație pentru 2026 dublează impozitul minim rezultat la rd. 47.

## Ce se greșește în practică

- **Se aplică cota IMCA de 1% pentru anul fiscal 2026**, în loc de 0,5% conform art. 18^1 alin. (16) — dublează suma de la rd. 47 și poate schimba greșit rezultatul comparației cu impozitul pe profit clasic.
- **Se completează rd. 39.1 (pierdere recuperată) și când rd. 38.1 e negativ.** Instrucțiunile OPANAF sunt explicite: doar dacă anul curent e pe profit.
- **Se aplică cota standard de 16% peste veniturile din baruri/cluburi de noapte/cazinouri**, deși art. 18 prevede o cotă separată de 5% pentru acele venituri, calculată distinct de restul profitului.

## Ce face iConta.eu

Lanțul complet rd. 22 → rd. 35 → rd. 38.1 → rd. 39/39.1 → rd. 40 → rd. 41.1 e calculat conform structurii din OPANAF 206/2025, cu cota standard de 16% (art. 17) și cota separată de 5% pentru baruri/cluburi de noapte (art. 18) confirmate.

Comparația cu impozitul minim pe cifra de afaceri (rd. 46/47/48) e calculată structural, cu pragul de eligibilitate de 50.000.000 euro verificat la cursul de la închiderea exercițiului financiar. **Cota efectiv folosită în formula IMCA pentru anul fiscal 2026 merită verificată separat** înainte de a considera finală suma de la rd. 47 — vezi [ghidul dedicat cotei IMCA din 2026](/ghid/imca-2026-cota-05-la-suta).

Vezi și: [pierderea fiscală reportată](/ghid/pierdere-fiscala-reportata) și [de la rezultatul contabil la rezultatul fiscal pe D101](/ghid/de-la-rezultatul-contabil-la-rezultatul-fiscal-d101).

[iConta.eu](/)
