---
title: "Ce curs valutar se folosește la recepția mărfii din UE?"
description: "Cursul BNR aplicabil la înregistrarea inițială a unei achiziții intracomunitare de marfă și de ce nu are legătură cu reevaluarea ulterioară a datoriei."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce curs valutar se folosește la recepția mărfii din UE?

La recepția mărfii cumpărate din UE, în valută, folosești cursul de schimb BNR comunicat pentru data la care are loc operațiunea — nu cursul din ziua în care ajunge factura la contabilitate și nu cursul din ultima zi a lunii. E vorba de înregistrarea inițială a tranzacției, un moment distinct de reevaluarea lunară a datoriei rămase.

## Temeiul legal

::: ghid-temei
„319. - O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii."
— OMFP 1802/2014, pct. 319 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- „Data efectuării operațiunii" e, în practică, data recepției mărfii (sau data facturii, dacă factura precedă recepția și marchează transferul de proprietate) — nu data plății către furnizorul din UE.
- Cursul folosit e cel comunicat de BNR pentru acea zi calendaristică; dacă operațiunea are loc într-o zi nebancară, se folosește cel mai recent curs comunicat anterior.
- Valoarea în lei rezultată la acest curs devine baza de înregistrare atât pentru stoc (cont 371/301, element nemonetar, care nu se mai modifică ulterior din cauza cursului), cât și pentru datoria față de furnizor (cont 401, element monetar).
- De aici încolo, datoria — nu marfa — urmează regulile de diferențe de curs: se reevaluează lunar la cursul BNR din ultima zi bancară a lunii (pct. 325) și generează diferență de curs (665/765) la decontare (pct. 322).

## Ce se greșește în practică

- Se folosește cursul din data plății facturii pentru înregistrarea inițială a mărfii, deși legea cere cursul de la data operațiunii (recepție/facturare), nu de la data decontării.
- Se reevaluează greșit valoarea stocului la finalul lunii, la cursul BNR curent — stocul e element nemonetar și rămâne la valoarea de intrare; doar datoria față de furnizor se reevaluează.
- Se ignoră diferența dintre cursul de la vamă/factura externă (dacă diferă de cursul BNR al zilei) și cursul oficial BNR, care e singurul relevant contabil pentru înregistrarea inițială.

## Ce face iConta.eu

Cursul BNR folosit la înregistrarea inițială a unei tranzacții în valută — inclusiv la recepția unei mărfi din UE — vine din `core/curs_bnr.py`, folosit în fluxul de facturare/achiziții, nu prin funcționalitatea de diferențe de curs valutar (F041). F041 (`core/diferente_curs.py`) intervine abia **după** înregistrarea inițială: la decontarea datoriei către furnizorul extern sau la reevaluarea ei lunară, calculând diferența 665/765 pe soldul rămas. Alegerea cursului la recepție nu e, deci, o funcție a F041, ci ține de ecranul de achiziții/facturare.

[iConta.eu](/)
