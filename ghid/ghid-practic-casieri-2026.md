---
title: "Ghid practic pentru casieri 2026"
description: "Plafoanele legale de numerar aplicabile în 2026, conform Legii 70/2015 actualizată prin Legea 239/2025, esențiale pentru orice casier."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ghid practic pentru casieri 2026

Munca de casier se reduce, din punct de vedere legal, la câteva reguli fixe despre numerar: cât poți încasa sau plăti într-o zi, de la cine, și ce e strict interzis. Restul e disciplină de operare a casei de marcat și de completare a registrului de casă.

## Temeiul legal

::: ghid-temei
„Articolul 3 (1) [...] se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: a) încasări de la persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei de la o persoană; [...] c) plăți către persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei/persoană, dar nu mai mult de un plafon total de 10.000 lei/zi [...]
Articolul 4 (1) Operațiunile de încasări în numerar efectuate de persoanele prevăzute la art. 1 alin. (1), de la persoane fizice [...] se efectuează în limita unui plafon zilnic de 10.000 lei de la o persoană."
— Legea 70/2015, art. 3 alin. (1) lit. a) și c), art. 4 alin. (1) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Cele patru plafoane pe care orice casier trebuie să le știe pe de rost, pentru 2026:

- **5.000 lei/zi** — încasare sau plată către o persoană juridică/entitate din art. 1 alin. (1) (firme, PFA, întreprinderi individuale/familiale, liber-profesioniști).
- **10.000 lei/zi** — plafon total de plăți către persoane juridice (chiar dacă suma per persoană rămâne sub 5.000 lei, totalul plăților zilei nu poate depăși 10.000 lei).
- **10.000 lei/zi** — încasare de la magazine de tip cash and carry, sau încasare de la o persoană fizică.
- **Interzisă fragmentarea** — împărțirea unei sume mari în tranșe, în aceeași zi sau în zile diferite, ca să pară fiecare tranșă sub plafon (art. 3 alin. (2)-(3)).

Plafoanele se aplică per **zi calendaristică** și per **relație cu partenerul**, nu per tură de lucru sau per casă de marcat — o firmă cu mai multe puncte de vânzare/case de marcat cumulează, la nivel de firmă, sumele încasate/plătite de la aceeași persoană în aceeași zi.

## Ce se greșește în practică

- Se ignoră plafonul total zilnic de 10.000 lei pentru plăți, concentrându-se doar pe plafonul de 5.000 lei/persoană — cele două limite se aplică simultan.
- Se tratează plafonul de 10.000 lei de la persoane fizice ca fiind identic cu cel de la persoane juridice (5.000 lei) — sunt plafoane diferite, pentru categorii diferite de parteneri.
- Se acceptă fragmentarea deliberată a unei încasări mari, crezând că respectă legea atâta timp cât fiecare tranșă individuală pare sub plafon.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **aplică plafoanele de numerar din Legea 70/2015, actualizată prin Legea 239/2025 (în vigoare de la 01.01.2026)**, direct în modulul de casierie (`core/casa.py`) — constantele `PLAFON_INCASARE_PJ`, `PLAFON_PLATA_PJ`, `PLAFON_PLATA_PJ_TOTAL` și `PLAFON_PF` reflectă exact valorile din lege, iar aplicația generează avertismente la depășirea lor, calculate cumulat pe zi, la nivel de firmă.

[iConta.eu](/)
