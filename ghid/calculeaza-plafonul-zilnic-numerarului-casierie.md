---
title: "Cum se calculează plafonul zilnic al numerarului din casierie?"
description: "Care sunt plafoanele legale pentru încasările și plățile în numerar ale unei firme, cum se calculează pe zi și pe partener."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează plafonul zilnic al numerarului din casierie?

Legea numerarului nu impune un singur plafon, ci mai multe, diferite după direcția operațiunii (încasare sau plată) și după tipul de partener. Calculul se face **pe zi și pe persoană**, nu pe total tranzacții ale firmei într-o zi.

## Temeiul legal

::: ghid-temei
„(1) Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: a) încasări de la persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei de la o persoană; b) încasări efectuate de către magazinele de tipul cash and carry [...] în limita unui plafon zilnic de 10.000 lei de la o persoană; c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi; d) plăți către magazinele de tipul cash and carry [...] în limita unui plafon zilnic total de 10.000 lei; e) plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare. (2) Sunt interzise încasările fragmentate în numerar de la beneficiari pentru facturile a căror valoare este mai mare de 5.000 lei [...], precum și fragmentarea facturilor pentru o livrare de bunuri sau o prestare de servicii a căror valoare este mai mare de 5.000 lei, respectiv de 10.000 lei."
— Legea nr. 70/2015, art. 3 alin. (1)-(2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

- **Încasări de la o persoană (juridică/PFA)**: maximum 5.000 lei pe zi de la aceeași persoană (10.000 lei dacă firma e de tip cash and carry).
- **Plăți către o persoană**: maximum 5.000 lei pe zi către aceeași persoană, dar cu un plafon total suplimentar de 10.000 lei pe zi indiferent de câte persoane sunt plătite.
- **Avansuri spre decontare**: maximum 5.000 lei pe zi, per persoană care a primit avansul — sumele acordate ca avans intră imediat în calculul plafonului zilnic.
- Fragmentarea unei facturi mai mari decât plafonul, în mai multe tranșe de încasare/plată în numerar, ca să „încapă" sub plafon, e interzisă explicit — diferența peste plafon trebuie achitată prin instrument de plată fără numerar (transfer bancar, card).
- Aceste plafoane sunt distincte de plafonul (mult mai mare, 50.000 lei/tranzacție) aplicabil operațiunilor de încasări/plăți în numerar **între persoane fizice**, care e un regim separat, reglementat de un alt articol al aceleiași legi.

## Ce se greșește în practică

- Se calculează plafonul pe total tranzacții zilnice ale casieriei, în loc de pe fiecare partener (persoană) în parte — poți încasa 5.000 lei de la partenerul A și alți 5.000 lei de la partenerul B, în aceeași zi, fără să încalci legea.
- Se ignoră faptul că plățile au un plafon dublu: 5.000 lei per persoană, dar și un plafon total de 10.000 lei/zi indiferent de câte persoane sunt plătite în numerar.
- Se fragmentează o factură mare în două chitanțe de sub 5.000 lei fiecare, considerând greșit că regula se referă la „operațiune", nu la valoarea totală a facturii/livrării.
- Se confundă plafonul dintre firme (5.000/10.000 lei) cu plafonul dintre persoane fizice (50.000 lei), aplicând din greșeală pe unul regulile celuilalt.

## Ce face iConta.eu

iConta.eu are un modul de casierie care implementează explicit aceste plafoane — constante separate pentru încasări de la persoane juridice (5.000 lei, respectiv 10.000 lei la cash and carry), plăți către persoane juridice (5.000 lei per partener, 10.000 lei plafon total pe zi) și avansuri spre decontare — și o funcție de verificare a plafonului care semnalează depășirile pe zi și pe partener, conform Legii 70/2015 art. 3.

[iConta.eu](/)
