---
title: "Simulare impozit micro vs impozit pe profit pentru 2026"
description: "Elementele legale care trebuie luate în calcul într-o simulare micro vs. profit pentru 2026: cote, bază de impozitare și eligibilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Simulare impozit micro vs impozit pe profit pentru 2026

O simulare corectă micro vs. profit pentru 2026 nu se rezumă la compararea a „1%" cu „16%" — trebuie combinate trei elemente legale distincte: cota, baza de impozitare și eligibilitatea, fiecare schimbată sau precizată prin OUG 8/2026.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Legea 227/2015, art. 51 alin. (1), astfel cum a fost modificat prin OUG nr. 89/2025, art. I pct. 4, în vigoare de la 01.01.2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită."
— Legea 227/2015, art. 52 alin. (1), astfel cum a fost modificat prin OUG nr. 8/2026, art. 6 pct. 20, în vigoare de la 25.02.2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Legea 227/2015, art. 17 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Elementele pe care simularea trebuie să le țină cont, toate confirmate pentru anul fiscal 2026:

- **Cota micro rămâne 1%** din 2026 (fostele cote diferențiate de 1%/3% după numărul de salariați au dispărut prin OUG 89/2025, care a abrogat vechiul alin. 1^1 al art. 51).
- **Plafonul de eligibilitate pentru micro a scăzut la 100.000 euro** de la 25.02.2026 (OUG 8/2026), de la fostul plafon de 500.000 euro — o firmă care se aștepta să rămână micro cu venituri de, de exemplu, 300.000 euro, nu mai e eligibilă din acel moment.
- **Baza de calcul e diferită**: la micro, veniturile din orice sursă (art. 53), impozitate integral chiar și pe pierdere; la profit, profitul impozabil (venituri minus cheltuieli deductibile), cu cota de 16% (art. 17).
- **Pragul de echivalență** dintre cele două regimuri e o marjă de profit de aproximativ 6,25% din venituri (1% ÷ 16%): sub acest procent, micro costă mai puțin; peste, profitul.

## Ce se greșește în practică

- Se simulează cu plafonul vechi de 500.000 euro, ignorând reducerea la 100.000 euro intrată în vigoare la 25.02.2026 — o firmă care depășește acest nou prag nu mai poate rămâne, de fapt, micro.
- Se compară doar cotele nominale (1% vs. 16%), fără a calcula efectiv impozitul pe fiecare bază (venituri, respectiv profit).
- Se ignoră faptul că trecerea între regimuri nu e liberă oricând în cursul anului — depinde de condițiile din art. 47-48 și de situațiile obligatorii din art. 52.

## Ce face iConta.eu

iConta.eu calculează efectiv, din datele contabile reale ale firmei, atât baza impozitului pe profit (motorul D100, rezultat fiscal cumulat de la începutul anului, conform art. 41), cât și baza impozitului micro (venituri din orice sursă, conform art. 53), cu cotele actualizate pentru 2026. La data acestui ghid, aplicația nu are un modul dedicat de simulare comparativă „micro vs. profit" care să genereze automat cele două scenarii pentru aceleași cifre — comparația se poate obține azi rulând separat cele două calcule reale, pe baza rulajelor introduse în aplicație.

[iConta.eu](/)
