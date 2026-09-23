---
title: "Cum se ține contabilitatea conturilor bancare în valută?"
description: Un cont bancar în valută (5124) se ține atât în lei, cât și în valuta lui — fiecare operațiune se înregistrează la cursul BNR din ziua ei, iar soldul se reevaluează lunar la cursul BNR din ultima zi bancară a lunii, cu diferența pe venituri/cheltuieli financiare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se ține contabilitatea conturilor bancare în valută?

Un cont bancar în valută nu se ține doar în moneda lui — se ține în paralel și în lei, pentru ca soldul să poată intra corect în balanța contabilă a firmei. Asta înseamnă două reguli distincte, care se aplică în momente diferite: cursul de la fiecare operațiune și cursul de la reevaluarea lunară a soldului.

## Temeiul legal

::: ghid-temei
„Creanțele și datoriile în valută, rezultate ca efect al tranzacțiilor entității, se înregistrează în contabilitate atât în lei, cât și în valută […]." — OMFP 1802/2014 (Reglementările contabile), pct. 314 alin. (1). „La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar" — pct. 325 alin. (1), aplicabil explicit și „disponibilităților în valută" conform alin. (2) lit. b).
:::

## Contul folosit

Disponibilul bancar în valută se ține în contul **5124**, distinct de 5121 (disponibil în lei). Fiecare încasare sau plată prin acest cont se înregistrează atât în moneda ei, cât și convertită în lei, la cursul BNR valabil la data operațiunii respective.

## Cele două momente de evaluare

1. **La fiecare operațiune** (încasare, plată) — cursul BNR din ziua operațiunii, conform regulii generale de înregistrare inițială a unei tranzacții în valută.
2. **La finalul fiecărei luni** — soldul rămas în cont se reevaluează la cursul BNR din ultima zi bancară a lunii, indiferent dacă au avut loc sau nu mișcări în acea lună. Diferența dintre soldul reevaluat și soldul de dinainte se înregistrează ca venit (765) sau cheltuială (665) din diferențe de curs.

Cele două reguli nu se substituie una alteia: operațiunile din timpul lunii rămân la cursul zilei fiecăreia, doar soldul rămas la final de lună se ajustează la cursul de închidere.

## Ce se greșește în practică

- Se omite reevaluarea lunară a soldului, tratând contul în valută ca și cum ar rămâne „înghețat" la cursurile operațiunilor individuale — regula pct. 325 cere reevaluarea explicită, lunar, chiar și fără mișcări noi.
- Se aplică un singur curs (de exemplu, cel de la începutul lunii) pentru toate operațiunile lunii, în loc de cursul BNR specific fiecărei zile de operațiune.
- Se confundă reevaluarea soldului (element monetar, lunar) cu evaluarea altor active în valută care nu sunt disponibilități bănești, cum ar fi stocurile — acelea sunt elemente nemonetare și nu se reevaluează în același fel.

## Ce face iConta.eu

Cursul BNR folosit la contabilizarea unei operațiuni în contul bancar în valută se determină pentru data operațiunii, prin motorul de curs (`core/curs_bnr.py`) — „ultimul curs BNR comunicat, valabil cel târziu la data cerută", fără fallback tăcut la un curs implicit dacă acesta nu poate fi determinat (curs indisponibil, prea vechi sau monedă necotată). Reevaluarea lunară a soldului în valută, cu recunoașterea diferenței pe 665/765, rămâne o regulă contabilă (pct. 325) pe care contabilul o aplică pe baza cursului BNR preluat din aceeași sursă.

[iConta.eu](/)
