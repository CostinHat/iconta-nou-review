---
title: "Cum optez pentru calculul anual al impozitului pe profit"
description: "Condițiile în care o firmă poate opta pentru sistemul anual de declarare și plată a impozitului pe profit, cu plăți anticipate trimestriale, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum optez pentru calculul anual al impozitului pe profit

Alternativa la declararea trimestrială clasică există, dar nu e o opțiune „din mers" — se exercită la începutul anului fiscal, e obligatorie pentru minimum doi ani și trebuie comunicată explicit către ANAF.

## Temeiul legal

::: ghid-temei
„(2) Contribuabilii, alții decât cei prevăzuți la alin. (4) și (5), pot opta pentru calculul, declararea și plata impozitului pe profit anual, cu plăți anticipate, efectuate trimestrial. [...] (3) Opțiunea pentru sistemul anual de declarare și plată a impozitului pe profit se efectuează la începutul anului fiscal pentru care se solicită aplicarea prevederilor alin. (2). Opțiunea este obligatorie pentru cel puțin 2 ani fiscali consecutivi. [...] Contribuabilii comunică organelor fiscale competente modificarea sistemului anual/trimestrial de declarare și plată a impozitului pe profit, potrivit prevederilor Codului de procedură fiscală, până la data de 31 ianuarie inclusiv a anului fiscal respectiv."
— Legea nr. 227/2015 (Codul fiscal), art. 41 alin. (2) și (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pașii concreți ai opțiunii:

- Firma trebuie să comunice ANAF modificarea sistemului, de la trimestrial la anual (sau invers), **până la 31 ianuarie inclusiv** a anului fiscal pentru care vrea să se aplice noul sistem.
- Odată exercitată, opțiunea pentru sistemul anual este **obligatorie minimum 2 ani fiscali consecutivi** — nu se poate reveni la trimestrial doar pentru că a fost mai convenabil un singur an.
- În sistemul anual, plățile către buget continuă să se facă **trimestrial**, ca plăți anticipate, dar calculul și definitivarea impozitului se fac o singură dată, la finalul anului, la termenul declarației anuale.
- Nu toți contribuabilii pot alege: instituțiile de credit (alin. (4)) și anumite categorii prevăzute la alin. (5) au un regim obligatoriu propriu, distinct de opțiunea generală.

## Ce se greșește în practică

- Se încearcă schimbarea sistemului de declarare în cursul anului fiscal, după 31 ianuarie, deși legea fixează acest termen ca dată-limită pentru comunicarea opțiunii.
- Se renunță la sistemul anual după un singur an, ignorând obligativitatea de minimum 2 ani fiscali consecutivi impusă de lege pentru menținerea opțiunii.
- Se confundă sistemul anual cu plăți anticipate (care tot presupune plăți trimestriale către buget) cu o scutire de plăți intermediare — diferența e doar în modul de calcul și declarare, nu în ritmul plăților.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează atât declarația trimestrială de impozit pe profit (D100), cât și declarația anuală (D101), din datele contabile introduse (`core/d100.py`, `core/d101.py`), dar **nu gestionează** opțiunea propriu-zisă pentru sistemul anual și nu depune comunicarea către ANAF privind schimbarea sistemului de declarare. Decizia de a opta pentru sistemul anual, respectarea termenului de 31 ianuarie și obligativitatea celor 2 ani consecutivi rămân responsabilitatea contabilului.

[iConta.eu](/)
