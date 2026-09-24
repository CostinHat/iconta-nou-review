---
title: "Când are nevoie o firmă IT de cod special de TVA?"
description: "Firmele IT neplătitoare de TVA care prestează sau achiziționează servicii intracomunitare au nevoie, de regulă, de codul special art. 317 CF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când are nevoie o firmă IT de cod special de TVA?

Multe firme IT mici (micro-întreprinderi, neplătitoare de TVA „normal") lucrează frecvent cu clienți sau furnizori din UE — livrează servicii software unei firme din alt stat membru sau cumpără abonamente/servicii digitale de la furnizori UE. Chiar și fără să fie plătitoare de TVA „clasic”, aceste firme au adesea nevoie de o înregistrare specială.

## Temeiul legal

::: ghid-temei
CF art. 317: „Înregistrare specială pentru neplătitori care fac AIC peste plafon sau servicii IC (alin. 1 lit. a-d). Alin. (1)-(2) modificate de OG 22/2025 art. I pct. 24, 01-09-2025.” (sursă: `cod_fiscal_227_2015_consolidat.txt`, L21049-21160+)
:::

Câmpul din profilul firmei descrie chiar acest scop: „Înregistrare specială în scopuri de TVA (art. 317 CF) pentru achiziții/livrări intracomunitare la neplătitori.” Adică o firmă IT neplătitoare de TVA obișnuit are nevoie de codul special art. 317 dacă, în activitatea ei curentă, prestează servicii către firme din UE sau primește servicii de la furnizori din UE — cazuri tipice pentru domeniul IT (dezvoltare pentru clienți străini, abonamente la unelte/servicii cloud facturate de furnizori din alt stat membru).

Această înregistrare specială decide, printre altele, obligația de a depune D390 (declarația recapitulativă VIES) și marchează firma ca `pers_inreg` în D301.

## Ce se greșește în practică

- Se presupune că, fiind neplătitoare de TVA, firma nu are nicio obligație legată de operațiunile cu parteneri din UE — de fapt, tocmai calitatea de neplătitor e cea care declanșează, în anumite condiții, nevoia codului special.
- Se confundă codul special art. 317 cu înregistrarea normală de plătitor de TVA (art. 316) — sunt regimuri diferite, cu efecte diferite.
- Se amână înregistrarea până „după ce apare o problemă”, deși ea trebuie făcută înainte sau odată cu prima operațiune relevantă.

## Ce face iConta.eu

Profilul firmei are un câmp dedicat, `inreg_art317`, descris explicit ca fiind pentru „achiziții/livrări intracomunitare la neplătitori”; el decide dacă D390 devine datorat corect și dacă firma apare marcată `pers_inreg` în D301.

Important de precizat: iConta **nu automatizează obținerea** codului special — câmpul e un flag manual, bifat de utilizator după ce înregistrarea a fost obținută efectiv la ANAF (formularul 700, depus prin SPV). Aplicația nu generează acest formular și nu interoghează SPV pentru înregistrare; rolul ei e să reflecte corect, în declarații, statutul deja obținut.

[iConta.eu](/)
