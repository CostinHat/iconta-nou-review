---
title: "Impozit micro pentru organizarea de evenimente"
description: "De la 1 ianuarie 2026 toate microîntreprinderile, inclusiv firmele din organizarea de evenimente sau cateringul pentru evenimente, plătesc o cotă unică de 1%, după eliminarea vechiului split 1%/3% pe coduri CAEN."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozit micro pentru organizarea de evenimente

O firmă care organizează evenimente (conferințe, târguri, petreceri corporate) sau care face catering pentru evenimente se întreabă frecvent dacă activitatea ei intră sub o cotă specială de impozit pe veniturile microîntreprinderilor. Răspunsul s-a schimbat radical de la 1 ianuarie 2026: vechea regulă cu cote diferite pe coduri CAEN a fost eliminată, iar azi se aplică o cotă unică pentru toate microîntreprinderile.

## Temeiul legal

::: ghid-temei
„Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— Codul fiscal (Legea 227/2015), art. 51 alin. (1), în forma aplicabilă de la 01.01.2026 (modificat de OUG 89/2025) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„b) 3%, pentru microîntreprinderile care: [...] 2. desfășoară activități, principale sau secundare, corespunzătoare codurilor CAEN: [...] 5610 - Restaurante, 5621 - Activități de alimentație (catering) pentru evenimente, 5629 - Alte servicii de alimentație n.c.a., 5630 - Baruri și alte activități de servire a băuturilor, [...]"
— Codul fiscal, art. 51 alin. (1) lit. b) pct. 2, formă introdusă de Legea 296/2023, abrogată de la 01.01.2026 de OUG 89/2025 (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

- De la 1 ianuarie 2026, OUG 89/2025 a eliminat complet vechiul split de cote 1%/3% pe coduri CAEN: toate microîntreprinderile plătesc 1%, indiferent de activitatea desfășurată.
- Până la 31 decembrie 2025, firmele cu codul CAEN 5621 (catering pentru evenimente) intrau automat în lista specială cu cotă de 3% — chiar dacă nu depășeau plafonul de venituri de 60.000 euro care declanșa 3% pentru restul microîntreprinderilor.
- Codul CAEN 8230 (activități de organizare a expozițiilor, târgurilor și congreselor — organizarea de evenimente propriu-zisă) **nu a fost niciodată** în lista specială, nici înainte, nici după 2026: firmele cu acest CAEN au aplicat mereu regula generală, în funcție doar de nivelul veniturilor.
- Ieșirea din regimul micro rămâne condiționată de un plafon de venituri: peste 100.000 euro într-un an fiscal, firma datorează impozit pe profit (16%) începând cu trimestrul depășirii (art. 52 alin. (1) CF, prag confirmat aplicabil pentru calculul de la trimestrul I 2026, potrivit OUG 8/2026).

## Ce se greșește în practică

- Se aplică din obișnuință vechea regulă „evenimente = cotă de 3%" și în 2026, deși de la 1 ianuarie nu mai există nicio diferențiere de cotă pe coduri CAEN.
- Se confundă codul CAEN de organizare de evenimente (8230) cu cel de catering pentru evenimente (5621) — doar al doilea a fost vreodată vizat de regula specială, și doar până la finalul lui 2025.
- Nu se urmărește plafonul de 100.000 euro cumulat de la începutul anului, mai ales la firme cu venituri concentrate sezonier (nunți de vară, festivaluri, sezon de conferințe de toamnă), unde câteva evenimente mari pot împinge rapid firma peste prag.

## Ce face iConta.eu

La calculul impozitului pentru firmele aflate în regim micro (declarația D100), iConta.eu aplică automat cota din registrul central de cote (`core/common.py`, cheia `"impozit_micro"`), citită prin `core/d100.py`. Registrul reține azi o singură valoare, 1%, valabilă din 2023, cu o notă explicită în cod care confirmă că OUG 89/2025 a eliminat de la 01.01.2026 splitul 1%/3% pe coduri CAEN și pragul de 60.000 euro asociat lui. Contabilul poate suprascrie manual cota dacă are un caz particular, dar nu există nicio logică în aplicație care să citească sau să diferențieze după codul CAEN al firmei — ceea ce, pentru 2026, corespunde exact legii: nu mai există nicio diferențiere de urmărit pe activitate.

[iConta.eu](/)
