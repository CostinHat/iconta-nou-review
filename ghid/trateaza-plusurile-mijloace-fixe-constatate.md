---
title: Cum se tratează plusurile de mijloace fixe constatate la inventar?
description: Un mijloc fix găsit în plus la inventariere se evaluează la valoare justă, intră pe contul 4754 și se înscrie efectiv în registrul de mijloace fixe — altfel rămâne invizibil pentru amortizare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se tratează plusurile de mijloace fixe constatate la inventar?

Un mijloc fix descoperit în plus la inventarierea anuală — un activ existent fizic, dar niciodată înregistrat corect în evidență — nu se tratează ca un plus obișnuit de marfă. El trebuie evaluat, înscris în registrul de mijloace fixe cu toate datele lui (durată, dată de punere în funcțiune, metodă de amortizare) și, abia apoi, pornit pe calculul amortizării.

## Temeiul legal

::: ghid-temei
„În situația constatării unor plusuri în gestiune, bunurile respective se evaluează potrivit reglementărilor contabile aplicabile."
— OMFP 2861/2009, Anexa 1, pct. 40 alin. (1)
:::

::: ghid-temei
„d) la valoarea justă - pentru bunurile obținute cu titlu gratuit sau constatate plus la inventariere."
— OMFP 1802/2014, pct. 75 alin. (1) lit. d)
:::

Evaluarea la valoare justă (nu la o valoare istorică, inexistentă pentru un bun nemai­înregistrat) e regula pentru orice plus constatat la inventar, mijloc fix sau nu. Diferența reală pentru un mijloc fix e că simpla evaluare nu e suficientă: dacă bunul nu ajunge înscris în registrul de mijloace fixe — cu durată normală de funcționare, dată de punere în funcțiune și metodă de amortizare compatibilă cu categoria lui (art. 28 din Codul fiscal) — el rămâne „invizibil" pentru calculul amortizării și pentru raportarea în SAF-T (secțiunea Active).

Contabil, plusul de mijloc fix se înregistrează pe un cont distinct de cel folosit pentru plusurile de stocuri: 4754 „Plusuri de inventar de natura imobilizărilor", parte din clasa conturilor de subvenții și venituri în avans. Fiind în această clasă, plusul nu intră integral și imediat la venituri impozabile în anul constatării — se reia treptat, pe măsura amortizării activului, ca la o subvenție pentru investiții. Codul sursă al aplicației nu are însă un mecanism explicit verificat pentru reluarea automată 4754→venituri; dacă reluarea nu se face automat în evidența ta, tratarea ei rămâne responsabilitatea contabilului.

## Ce se greșește în practică

- Se înregistrează plusul doar ca notă contabilă (4754 = 21x), fără să se completeze și registrul de mijloace fixe cu durata, data PIF și metoda — activul rămâne fără amortizare calculată de acolo încolo.
- Se evaluează plusul la o valoare arbitrară sau la costul unui bun similar cumpărat recent, în loc de valoarea justă cerută explicit de normă.
- Se presupune că plusul de mijloc fix se tratează contabil identic cu un plus de marfă (cont 371=607) — regimul e diferit: cont 4754, clasă de venituri în avans, nu un venit direct din exploatare.

## Ce face iConta.eu

Operațiunea „Plus mijloc fix" din ecranul „Inventariere anuală" generează nota contabilă pe contul 4754 și, în același pas, înscrie activul în registrul de mijloace fixe al firmei — cu durata normală de funcționare și data de punere în funcțiune introduse ca și câmpuri obligatorii. Dacă metoda de amortizare aleasă nu e permisă pentru categoria activului (derivată din contul de imobilizare), operațiunea e refuzată explicit, nu acceptată cu o metodă liniară „ghicită" în locul ei. Odată înregistrat, activul apare în „Firmă > Mijloace fixe", cu amortizarea calculată de același motor folosit pentru toate celelalte active ale firmei.

[iConta.eu](/)
