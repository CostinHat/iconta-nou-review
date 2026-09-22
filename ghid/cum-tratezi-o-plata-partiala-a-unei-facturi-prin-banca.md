---
title: Cum tratezi o plată parțială a unei facturi prin bancă?
description: Când o încasare sau o plată nu acoperă integral o factură, motorul alocă suma FIFO și marchează linia galbenă pentru confirmare manuală; dacă firma e pe TVA la încasare, TVA-ul exigibil se calculează separat pentru fiecare sumă efectiv încasată, conform art. 282 alin. (8) Cod fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum tratezi o plată parțială a unei facturi prin bancă?

Nu orice încasare sau plată acoperă integral suma unei facturi. Când clientul plătește mai puțin decât soldul facturii, sau plătește o sumă care nu corespunde exact niciunei facturi sau combinații de facturi, motorul de matching din iConta.eu tratează cazul ca plată parțială.

## Temeiul legal

::: ghid-temei
**Articolul 282** [...] **(3)** Prin excepție de la prevederile alin. (1) și alin. (2) lit. a), exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens, denumite în continuare persoane care aplică sistemul TVA la încasare. Plafonul pentru aplicarea sistemului TVA la încasare este de: a) 5.000.000 lei, în perioada 1 martie-31 decembrie 2026; b) 5.500.000 lei, începând cu data de 1 ianuarie 2027.

**(8)** Pentru determinarea taxei aferente încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, care devine exigibilă potrivit prevederilor alin. (3), fiecare încasare totală sau parțială se consideră că include și taxa aferentă.
:::

## Cum alocă motorul o plată parțială

Dacă nu există nicio potrivire exactă (nici pe o singură factură, nici pe o combinație de 2-4 facturi), motorul alocă suma liniei de extras secvențial, pe facturile deschise ale partenerului, în ordinea vechimii (FIFO). Există două situații posibile, ambele marcate galben, necesitând confirmare manuală înainte de contare: suma liniei depășește totalul soldurilor deschise ale partenerului, caz în care rămâne un rest nealocat; sau suma se consumă integral prin alocare parțială, ultima factură atinsă rămânând doar parțial acoperită.

::: ghid-exemplu
O factură de 1.000 lei rămâne deschisă. Clientul plătește 600 lei. Motorul nu găsește potrivire exactă, așa că alocă cei 600 lei ca plată parțială pe factura respectivă — soldul rămas deschis e 400 lei, iar linia din extras primește status galben, pentru confirmare.
:::

Dacă firma aplică sistemul TVA la încasare, fiecare sumă alocată printr-o plată parțială devine bază separată de calcul pentru TVA exigibil — nu se așteaptă încasarea integrală a facturii pentru a considera TVA exigibilă. Cota de TVA aplicată e cea de pe liniile facturii; dacă factura nu are cotă de TVA setată pe liniile ei, calculul nu poate porni.

## Ce se greșește în practică

- Se așteaptă ca sistemul să lase automat linia "în așteptare" până apare restul de plată — de fapt suma parțială primită trebuie confirmată și contată separat, ca alocare parțială.
- Se calculează TVA la încasare pe totalul facturii, nu pe suma efectiv încasată la acea plată parțială — contrar art. 282 alin. (8).
- Se confundă statusul galben (alocare parțială, necesită confirmare manuală) cu o eroare a sistemului, deși e comportamentul normal pentru o sumă care nu se potrivește exact.
- Se ignoră faptul că, odată contată o alocare, factura afectată nu mai are disponibil integral la liniile viitoare din același extras — soldul e deja diminuat.

## Ce face iConta.eu

`_alocare_fifo` din `core/reconciliere.py` distribuie suma liniei pe facturile deschise ale partenerului, în ordine FIFO, marcând rezultatul galben. La contare (`conteaza` din `core/reconciliere_api.py`), fiecare alocare parțială generează o înregistrare separată legată de `factura_id`; dacă firma are activ profilul `tva_la_incasare`, TVA-ul exigibil pentru acea alocare se calculează separat, prin `core.tva_incasare.tva_din_incasare`, folosind cota de pe liniile facturii — lipsa cotei declanșează o eroare explicită la contare.

[iConta.eu](/)
