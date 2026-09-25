---
title: "Cum tratez fiscal reevaluarea creanțelor și datoriilor în valută?"
description: "Reevaluarea lunară e o obligație contabilă (OMFP 1802/2014); la impozit pe profit, diferența rezultată urmează regula generală a rezultatului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez fiscal reevaluarea creanțelor și datoriilor în valută?

Aici sunt de fapt două întrebări distincte, ușor de confundat: dacă trebuie să faci reevaluarea (da, obligatoriu, lunar, contabil) și cum se impozitează diferența rezultată (depinde de regimul fiscal al firmei). Reevaluarea în sine nu e o alegere fiscală — e o normă contabilă. Ce e fiscal e doar tratamentul diferenței obținute.

## Temeiul legal

::: ghid-temei
„325. - (1) La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz."
— OMFP 1802/2014, pct. 325 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Reevaluarea lunară e o obligație contabilă generală, aplicabilă tuturor firmelor care conduc contabilitate potrivit OMFP 1802/2014, indiferent de regimul de impozitare (profit sau micro) — nu e o opțiune fiscală de exercitat sau nu.
- Diferența rezultată (665 sau 765) se **impozitează diferit** în funcție de regim: la impozit pe profit, intră în rezultatul fiscal fără corecție specială (art. 19 alin. (1) Cod fiscal); la microîntreprinderi, se scade din baza impozabilă lunară (art. 53 alin. (1) lit. h), cu regularizare în trimestrul IV (art. 53 alin. (2) lit. b).
- Nu există o „opțiune" de a nu reevalua din motive fiscale — omiterea reevaluării e o abatere contabilă, nu o alegere de optimizare fiscală legitimă.
- Diferența dintr-o reevaluare lunară care ulterior se inversează (cursul revine) nu se „anulează" retroactiv — fiecare lună își păstrează propria diferență recunoscută, la propriul curs de referință.

## Ce se greșește în practică

- Se amână reevaluarea lunară, motivat greșit de ideea că „oricum diferența finală se vede la decontare" — dar reevaluarea lunară și diferența la decontare sunt două obligații distincte, cumulative, nu alternative.
- Se aplică regula fiscală de la impozit pe profit (fără corecție) și firmelor la microîntreprinderi, ignorând scăderea explicită din baza impozabilă prevăzută de art. 53.
- Se tratează diferența din reevaluare ca fiind „doar informativă", fără impact fiscal, deși ea influențează direct rezultatul contabil de la care pornește calculul fiscal.

## Ce face iConta.eu

Reevaluarea lunară e automatizată prin ecranul „Operațiuni speciale → Reevaluare valuta": aplicația ia cursul BNR pentru fiecare monedă din listă și generează, prin `core/diferente_curs.py` (`reevaluare_sold`), o singură notă contabilă cu toate diferențele pe 665/765. Partea fiscală **nu e automatizată**: aplicația nu calculează impozitul pe profit și nu aplică regula de scădere din baza impozabilă micro — sumele generate de reevaluare rămân în balanța contabilă, de unde contabilul le preia manual în calculul fiscal, în funcție de regimul de impozitare al firmei.

[iConta.eu](/)
