---
title: Cum tratezi o încasare parțială de la client?
description: O încasare parțială declanșează exigibilitate proporțională, calculată prin metoda sutei mărite — restul facturii rămâne pe 4428 până la următoarea plată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratezi o încasare parțială de la client?

Nu trebuie să aștepți plata integrală a unei facturi ca să raportezi TVA — fiecare sumă primită, oricât de mică, generează o porție de TVA exigibilă imediat.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3) CF**: „[...] exigibilitatea taxei intervine la data încasării contravalorii **integrale sau parțiale** a livrării de bunuri ori a prestării de servicii [...]" Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, linia 17635.

**Art. 282 alin. (8) CF**: „[...] fiecare încasare totală sau parțială se consideră că include și taxa aferentă." Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, liniile 17727-17729.
:::

Practic, fluxul e în doi pași. La facturare, dacă suma nu a fost încă încasată, TVA merge pe contul 4428 „TVA neexigibilă" (nu pe 4427). Când vine o încasare parțială, se calculează TVA aferentă exact acelei sume, prin metoda sutei mărite (suma încasată × cotă/(100+cotă)), și doar acea porție trece din 4428 în 4427 „TVA colectată" — restul rămâne mai departe pe 4428, până la următoarea încasare.

Ecranul dedicat din aplicație confirmă exact acest mecanism contabil: pentru sensul „încasare", nota generează articolul 4428 = 4427, pentru suma exigibilă calculată la acea plată.

Dacă factura are mai multe cote de TVA sau regimuri de impozitare diferite, iar suma încasată nu acoperă toate liniile, ai dreptul să alegi ce consideri încasat, pentru a determina corect alocarea pe cote (conform Normelor metodologice de aplicare a Codului fiscal, HG 1/2016).

## Ce se greșește în practică

- Se amână complet înregistrarea TVA până la încasarea integrală a facturii, deși legea cere exigibilitate proporțională la fiecare încasare parțială.
- Se calculează TVA aferentă încasării parțiale ca procent din baza facturii, nu prin metoda sutei mărite aplicată sumei efectiv încasate.
- Se pierde alocarea corectă pe cote la facturile cu cote multiple, prin împărțire proporțională automată, în loc de alegerea explicită permisă de normă.

## Ce face iConta.eu

Ecranul manual „TVA la încasare" (rută `nota-tva-incasare`) generează articolul contabil 4428=4427 pentru sensul „încasare", pe baza sumei și datei introduse de contabil, calculate cu formula sutei mărite din `core/tva_incasare.py`. Pentru firmele cu decontări alocate automat pe facturi, motorul `core/d300.py` trece sumele prin aceeași funcție, cotă cu cotă, generând direct baza exigibilă și TVA exigibilă corespunzătoare fiecărei încasări parțiale.

[iConta.eu](/)
