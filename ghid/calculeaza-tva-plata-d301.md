---
title: Cum se calculează TVA de plată prin D301?
description: TVA-ul din D301 se calculează pe fiecare operațiune (bază × cotă), cu cota standard sau redusă valabilă la data exigibilității, iar servicii intracomunitare (secțiunea 4.1) se însumează și în totalul secțiunii 4.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează TVA de plată prin D301?

TVA-ul de plată prin decontul special nu e o singură formulă globală, ci suma taxei calculate pentru fiecare operațiune în parte, la cota valabilă în perioada în care ia naștere exigibilitatea taxei.

## Temeiul legal

::: ghid-temei
Pentru baza de impozitare: "se calculează coloana 2 x coloana 4" — OPANAF nr. 592/2016, Anexa 1 (coloana 2 = valoare în valută, coloana 4 = curs de schimb)
:::

::: ghid-temei
"nivelul acesteia este 21%" — Codul fiscal, Legea nr. 227/2015, art. 291 alin. (1), astfel cum a fost modificat de Legea nr. 141/2025, în vigoare de la 1 august 2025
:::

::: ghid-temei
"Cota aplicabilă pentru achiziții intracomunitare de bunuri este cota aplicată pe teritoriul României pentru livrarea aceluiași bun și care este în vigoare la data la care intervine exigibilitatea taxei." — Codul fiscal, art. 291 alin. (8)
:::

Pentru fiecare operațiune: baza de impozitare = valoarea în valută × cursul de schimb, iar TVA = baza × cota aplicabilă (standard 21% sau redusă 11%, ambele valabile la data exigibilității taxei, nu la data documentului). Pentru operațiunile din secțiunea 4.1 (servicii intracomunitare), norma cere ca ele să fie preluate și în totalul secțiunii 4, întrucât secțiunea 4.1 e un subset al secțiunii 4 — nu se adună de două ori TVA-ul, dar totalul secțiunii 4 include automat și sumele din 4.1.

## Ce se greșește în practică

- Se aplică o singură cotă "globală" pentru toată declarația, în loc de cota valabilă la data exigibilității fiecărei operațiuni în parte.
- Se ignoră regula de rollup: totalul secțiunii 4 trebuie să includă și sumele din secțiunea 4.1, nu doar operațiunile introduse direct la tipul 4.
- Se confundă suma de control de pe formular (verificare aritmetică a totalurilor) cu TVA-ul efectiv de plată — sunt lucruri diferite.

## Ce face iConta.eu

Cota se preia automat, period-aware, din configurația firmei (standard sau redusă, cu deduplicarea istoricului 9%/5% → 11% unificat de la 1 august 2025); dacă nicio cotă redusă nu e configurată pentru perioadă, opțiunea nu apare deloc în listă, ca să nu se ofere o valoare inexistentă. La generare, fiecare operațiune de tip 5 e adunată automat și în totalul de tip 4, conform regulii din normă — contabilul nu trebuie să facă manual această însumare.

[iConta.eu](/)
