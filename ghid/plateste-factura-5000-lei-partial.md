---
title: "Cum se plătește o factură de peste 5.000 lei parțial cash și parțial prin bancă?"
description: "Regula din Legea 70/2015 privind combinarea plății în numerar cu plata prin bancă pentru facturile care depășesc plafonul legal de 5.000 lei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se plătește o factură de peste 5.000 lei parțial cash și parțial prin bancă?

O factură de peste 5.000 lei, emisă de un furnizor persoană juridică (sau PFA/II/IF), nu poate fi achitată integral în numerar — dar poate, și practic trebuie, să fie achitată combinat: până la 5.000 lei în numerar, iar restul, obligatoriu, prin instrumente de plată fără numerar (transfer bancar, card etc.).

## Temeiul legal

::: ghid-temei
„Sunt interzise plățile fragmentate în numerar către furnizorii de bunuri și servicii pentru facturile a căror valoare este mai mare de 5.000 lei și, respectiv, de 10.000 lei, către magazinele de tipul cash and carry. Persoanele prevăzute la art. 1 alin. (1) pot achita facturile cu valori care depășesc plafonul de 5.000 lei, către furnizorii de bunuri și servicii, respectiv de 10.000 lei, către magazinele de tipul cash and carry, astfel: 5.000 lei/10.000 lei în numerar, suma care depășește acest plafon putând fi achitată numai prin instrumente de plată fără numerar."
— Legea nr. 70/2015, art. 3 alin. (3) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Mecanismul, explicat:

- Plafonul de 5.000 lei în numerar (art. 3 alin. (1) lit. c)) se aplică **per zi, per persoană** (furnizor), nu per factură — dar pentru o singură factură care depășește acest cuantum, legea permite explicit achitarea combinată: 5.000 lei cash + diferența prin bancă.
- Este interzisă **fragmentarea** plății numerar pentru a evita plafonul (de exemplu, plata a 5.000 lei azi și încă 3.000 lei numerar mâine, pentru aceeași factură) — art. 3 alin. (3) prima teză.
- Pentru magazinele de tip cash and carry, plafonul numerar admis este mai mare: 10.000 lei, cu aceeași regulă a combinării cu plata fără numerar pentru diferență.
- Regula simetrică se aplică și încasărilor (art. 3 alin. (2)): un furnizor nu poate încasa numerar peste 5.000 lei/10.000 lei de la același client, în aceeași zi, pentru aceeași factură.

## Ce se greșește în practică

- Se încearcă achitarea integrală în numerar a unei facturi de peste 5.000 lei, considerând că legea interzice doar plățile de peste 5.000 lei „per zi", nu neapărat per factură — de fapt, exact fragmentarea facturii pe mai multe zile este ceea ce legea interzice explicit.
- Se ignoră faptul că suma care depășește plafonul **trebuie** achitată prin instrument fără numerar — nu este o opțiune a plătitorului să aleagă alt numerar suplimentar prin altă tranzacție.
- Se confundă plafonul de 5.000 lei (persoane juridice/PFA) cu cel de 10.000 lei aplicabil operațiunilor cu persoane fizice (art. 4) sau cu cel de 10.000 lei pentru magazinele cash and carry (art. 3).

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un modul dedicat de casierie (`core/casa.py`, funcția `verifica_plafon`) care verifică automat, pe baza operațiunilor introduse, respectarea plafoanelor din Legea 70/2015: încasări/plăți zilnice către/de la persoane juridice (5.000 lei, 10.000 lei pentru cash and carry), plăți din avansuri spre decontare și soldul de casă. Când o sumă introdusă depășește plafonul legal, aplicația semnalează un avertisment (risc la control), fără să blocheze operațiunea — decizia de a împărți plata între numerar și bancă rămâne, ca și până acum, a contabilului.

[iConta.eu](/)
