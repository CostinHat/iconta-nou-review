---
title: De la rezultatul contabil la rezultatul fiscal în D101
description: D101 pleacă de la rezultatul contabil (rd. 22) și ajunge la profitul impozabil (rd. 40) printr-un lanț fix de rânduri din OPANAF 206/2025, taxat apoi cu cota de 16% de la art. 17 Cod fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum ajung de la rezultatul contabil la profitul impozabil în D101?

Rezultatul din balanță și impozitul pe profit datorat aproape niciodată nu sunt aceeași sumă înmulțită cu 16%. Între cele două stă un lanț de ajustări fiscale — cheltuieli nedeductibile adunate înapoi, elemente scăzute sau adăugate separat, pierderea din anii precedenți scăzută la final. D101 e formularul care face vizibil, rând cu rând, acest drum de la rezultatul contabil la baza de calcul a impozitului.

## Temeiul legal

::: ghid-temei
**OPANAF 206/2025, rd. 35-40:** *„35 Total profit impozabil/pierdere fiscală pentru anul de raportare, înainte de ajustarea cu pierderile curente (rd. 22 + rd. 34) ... 381 [=38.1] Profit impozabil/pierdere fiscală, înainte de reportarea pierderii din anii precedenţi (rd. 35 + rd. 36 + rd. 37 - rd. 38) ... 39 Pierdere fiscală de recuperat din anii precedenţi ... 391 [=39.1] Pierdere fiscală de recuperat în anul curent ... 40 Profit impozabil aferent anului de raportare (rd. 381 - rd. 391)"*

**OPANAF 206/2025, rd. 41.1:** *„41.1 Impozit aferent profitului ce se impune cu cota de 16%"*

**CF art. 17** — cota de bază: *„Cota de impozitare. Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."*
:::

## Lanțul complet, rând cu rând

```
rd.22   = rezultatul contabil (profit/pierdere din balanță)
rd.34   = total cheltuieli nedeductibile (suma rd.23...rd.33)
rd.35   = rd.22 + rd.34
rd.38.1 = rd.35 + rd.36 + rd.37 - rd.38     (alte ajustări: deduceri, venituri neimpozabile ș.a.)
rd.39.1 = pierdere fiscală recuperată din anii precedenți (≤ rd.39, doar dacă rd.38.1 e profit)
rd.40   = rd.38.1 - rd.39.1                  (profitul impozabil)
rd.41.1 = rd.40 × 16%                        (impozitul pe profit, cota de la art.17)
```

Pornești de la **rd. 22**, care e strict rezultatul contabil — ce arată contul de profit și pierdere. De acolo, formularul adaugă înapoi cheltuielile nedeductibile (rd. 34), pentru că acestea au redus rezultatul contabil dar nu au voie să reducă și baza fiscală. Rezultă rd. 35.

Peste rd. 35 se aplică alte ajustări (rd. 36-38) — venituri neimpozabile, deduceri suplimentare, alte elemente prevăzute de lege — și rezultă rd. 38.1, profitul (sau pierderea) *înainte* de reportarea pierderilor din anii anteriori.

Doar dacă rd. 38.1 e pozitiv se scade pierderea fiscală de recuperat (rd. 39.1), și abia atunci rezultă rd. 40 — baza reală pe care se aplică cei 16% de la art. 17.

## Contabil vs. fiscal, în conturi

În evidența contabilă, rezultatul (rd. 22) vine din soldul contului **121 „Profit sau pierdere"**. Impozitul calculat la rd. 41.1 se înregistrează în **691 „Cheltuieli cu impozitul pe profit"**, cu obligația de plată reflectată în **441 „Impozitul pe profit"**. Diferența dintre rd. 22 și rd. 40 e exact motivul pentru care impozitul pe profit nu se poate calcula direct din rulajul contului de rezultat, fără parcurgerea lanțului fiscal.

## Ce se greșește în practică

- **Se aplică 16% direct pe rezultatul contabil (rd. 22)**, sărind peste ajustările cu cheltuielile nedeductibile — impozitul iese subevaluat.
- **Se scade pierderea reportată (rd. 39.1) chiar și când rd. 38.1 e negativ.** Instrucțiunile spun explicit: rândul se completează „numai în situaţia în care se declară profit (rândul 381)".
- **Se confundă cheltuiala contabilă cu impozitul cu 441 direct**, fără să treacă întâi prin 691 — ordinea corectă e cheltuială (691) care generează obligația (441), nu invers.

## Ce face iConta.eu

Calculul urmează exact lanțul din instrucțiunile OPANAF 206/2025: rd. 22 → rd. 35 (cu rd. 34, total cheltuieli nedeductibile) → rd. 38.1 → rd. 39/39.1 (aplicat doar când rd. 38.1 e profit) → rd. 40, cota de 16% de la art. 17 fiind aplicată abia la final, pe rd. 40.

Vezi și: [cheltuielile deductibile la impozitul pe profit](/ghid/cheltuieli-deductibile-impozit-profit) și [pierderea fiscală reportată](/ghid/pierdere-fiscala-reportata).

[iConta.eu](/)
