---
title: "Cum reevaluez la sfârșitul lunii un credit în valută?"
description: "Regula contabilă pentru reevaluarea lunară a creditelor și datoriilor în valută, la cursul BNR din ultima zi bancară a lunii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum reevaluez la sfârșitul lunii un credit în valută?

Firmele care au contractat un credit în euro, dolari sau altă valută trebuie să-i recalculeze lunar valoarea în lei, pentru că soldul datoriei nu rămâne constant — se modifică odată cu cursul de schimb. Reglementările contabile stabilesc exact la ce curs se face această reevaluare și cum se înregistrează diferența rezultată.

## Temeiul legal

::: ghid-temei
„La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz."
— OMFP 1802/2014, Reglementări contabile, pct. 325 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat concret la un credit în valută:

- **Reevaluarea e obligatorie lunar**, nu doar la finalul exercițiului financiar — soldul creditului (principal rămas de rambursat, eventual și dobânda calculată dar neplătită, dacă e exprimată tot în valută) se recalculează la finele fiecărei luni.
- Cursul de utilizat e cel **comunicat de BNR din ultima zi bancară a lunii** — nu cursul mediu lunar, nu cursul BCE, nu cursul de la data acordării creditului.
- Diferența dintre soldul recalculat la noul curs și soldul înregistrat anterior în contabilitate se recunoaște ca **diferență de curs valutar**: cheltuială (contul 665, respectiv analiticul 6651 „Diferențe nefavorabile de curs valutar legate de elementele monetare exprimate în valută") dacă leul s-a depreciat față de valuta creditului, sau venit (contul 765/7651) dacă leul s-a apreciat.
- Regula acoperă atât creditele bancare, cât și orice altă datorie sau creanță exprimată în valută — un element monetar, în sensul reglementărilor, e orice sumă de bani sau drept/obligație de a primi/plăti o sumă fixă sau determinabilă.

## Ce se greșește în practică

- Se reevaluează creditul doar la 31 decembrie, „o dată pe an" — deși regula cere reevaluare la finele fiecărei luni, indiferent de mărimea firmei sau de dimensiunea creditului.
- Se folosește cursul de la data acordării creditului sau un curs mediu ales arbitrar, în loc de cursul BNR din ultima zi bancară a lunii de referință.
- Diferența de curs se înregistrează direct pe rezultatul reportat sau se ignoră complet dacă e nesemnificativă, deși legea nu prevede vreun prag de minimis pentru elementele monetare în valută — orice diferență se recunoaște.
- Se confundă diferența de curs din reevaluarea soldului rămas (element monetar, recalculat lunar) cu diferența de curs din decontarea efectivă a unei rate (care apare doar la momentul plății, la cursul zilei plății).

## Ce face iConta.eu

Acest subiect ține de reevaluarea valutară a creditelor bancare, o operațiune de contabilitate generală — nu de funcționalitatea F086 (sponsorizări și credit fiscal) cercetată pentru acest ghid, care privește exclusiv creditul fiscal obținut din sponsorizare (o reducere de impozit pe profit), fără nicio legătură cu creditele bancare sau cu reevaluarea valutară. Cercetarea disponibilă a verificat direct în cod doar motorul de sponsorizări și garda de plafon din D101 (`core/sponsorizari.py`, `core/d101.py`); nu avem, în acest dosar, o verificare a vreunui modul din iConta.eu pentru reevaluarea lunară a datoriilor în valută, așa că nu facem nicio afirmație despre existența sau absența unei asemenea automatizări.

[iConta.eu](/)
