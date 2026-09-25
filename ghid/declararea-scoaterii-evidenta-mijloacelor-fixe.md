---
title: "Declararea scoaterii din evidență a mijloacelor fixe la ANAF"
description: "Cum tratează Codul fiscal scoaterea din funcțiune a unui mijloc fix amortizabil și unde se reflectă efectul ei fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Declararea scoaterii din evidență a mijloacelor fixe la ANAF

Când un mijloc fix e vândut sau scos din funcțiune (casat), firma nu depune o declarație separată la ANAF doar pentru acest eveniment — efectul lui fiscal se reflectă în calculul impozitului pe profit, prin câștigul sau pierderea rezultată din operațiune, calculat pe baza valorii fiscale rămase neamortizate.

## Temeiul legal

::: ghid-temei
„Pentru mijloacele fixe amortizabile, deducerile de amortizare se determină fără a lua în calcul amortizarea contabilă. Câștigurile sau pierderile rezultate din vânzarea ori din scoaterea din funcțiune a acestor mijloace fixe se calculează pe baza valorii fiscale a acestora, diminuată cu amortizarea fiscală, cu excepția celor prevăzute la alin. (14)."
— Codul fiscal (Legea 227/2015), art. 28 alin. (17) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă practic:

- Scoaterea din funcțiune (casarea) a unui mijloc fix amortizabil nu declanșează o declarație fiscală distinctă — efectul ei apare în calculul rezultatului fiscal al perioadei, ca venit sau cheltuială, în funcție de diferența dintre valoarea fiscală rămasă neamortizată și eventualele sume încasate din valorificare.
- Baza de calcul e **valoarea fiscală**, nu valoarea contabilă — cele două pot diferi dacă amortizarea contabilă și cea fiscală au fost calculate diferit.
- Efectul ajunge, în cele din urmă, în declarația de impozit pe profit (D101), ca parte din calculul general al rezultatului fiscal al anului, nu printr-o formă separată de raportare.
- Pentru firmele care depun D406 (SAF-T), mișcarea de scoatere din evidență a activelor imobilizate se reflectă structural în secțiunea dedicată activelor fixe, ca parte a evidenței lunare/anuale a mijloacelor fixe raportate.

## Ce se greșește în practică

- Se caută o declarație specifică „de scoatere din evidență a mijlocului fix" la ANAF — nu există o asemenea formă separată; efectul e integrat în calculul impozitului pe profit.
- Se calculează câștigul/pierderea din casare pe baza valorii contabile, nu a valorii fiscale rămase neamortizate — cele două pot diferi, mai ales când firma a aplicat metode de amortizare accelerată sau alte facilități fiscale.
- Se confundă scoaterea din evidență a unui mijloc fix cu scoaterea din evidența persoanelor înregistrate în scopuri de TVA (art. 316 din Codul fiscal) — sunt proceduri complet diferite, cu temeiuri diferite.
- Se omite documentul justificativ al casării (proces-verbal) — fără el, cheltuiala/venitul din operațiune poate fi contestat la control ca nefundamentat.

## Ce face iConta.eu

iConta.eu are un modul dedicat calculului amortizării mijloacelor fixe (`core/d406_active.py`), care determină amortizarea acumulată la o dată dată, pe metoda aleasă pentru fiecare activ (liniară, degresivă etc.), și generează structura XML necesară raportării activelor în D406 (SAF-T). Modulul calculează amortizarea „la zi" pentru scenarii precum casarea sau reevaluarea unui mijloc fix, dar nu depune o declarație separată la ANAF doar pentru scoaterea din evidență — efectul fiscal al operațiunii ajunge, ca și în lege, în calculul impozitului pe profit al perioadei.

[iConta.eu](/)
