---
title: "e-Factura pentru decontarea cheltuielilor de deplasare"
description: "Ce legătură există, de fapt, între obligațiile de facturare electronică și decontarea cheltuielilor de transport, cazare și diurnă — și de ce cele două rămân procese separate în iConta."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# e-Factura pentru decontarea cheltuielilor de deplasare

Titlul acesta amestecă, de fapt, două fluxuri fiscale distincte. Un decont de deplasare grupează cheltuieli de transport, cazare și indemnizația de delegare (diurna) — unele dintre ele justificate cu facturi primite de la furnizori (hoteluri, transportatori), altele (diurna) fără nicio factură, fiindcă e o sumă calculată, nu o achiziție. Facturarea electronică e o obligație separată, care privește circuitul facturilor B2B, nu decontul intern al salariatului.

## Temeiul legal

::: ghid-temei
„k) indemnizația de delegare, indemnizația de detașare, [...] precum și orice alte sume de aceeași natură, altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare, primite de salariați potrivit legislației în materie, pe perioada desfășurării activității în altă localitate, în țară sau în străinătate, în interesul serviciului, pentru partea care depășește plafonul neimpozabil stabilit [...]"
— Codul fiscal, art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie separat clar:

- **Diurna** (indemnizația de delegare) este o sumă calculată pe zi de deplasare, plafonată neimpozabil conform art. 76 alin. (2) lit. k) CF — **nu are corespondent într-o factură**, deci nu poate face obiectul unei obligații de e-Factura.
- **Cheltuielile de transport și cazare** decontate în cadrul deplasării sunt, de regulă, susținute de facturi emise de furnizori (hoteluri, companii de transport) — acele facturi intră, ca orice altă factură primită de firmă, sub regulile generale de facturare electronică aplicabile relațiilor B2B, dar aceasta e o obligație a furnizorului care emite factura, nu a firmei care decontează cheltuiala angajatului.
- Decontul de deplasare în sine este un **document intern** al firmei (o notă de justificare a unui avans, cu anexarea documentelor de cheltuială) — nu e o factură și nu se depune în sistemul RO e-Factura ca atare.

## Ce se greșește în practică

- Se crede că decontul de deplasare trebuie „trecut prin e-Factura" — decontul nu e o factură, e un document contabil intern.
- Se ignoră obligația reală de e-Factura pentru facturile primite de la furnizorii de cazare/transport, care sunt facturi B2B obișnuite, supuse regulilor generale.
- Se presupune că diurna are nevoie de o „factură" justificativă — diurna e o sumă calculată legal, nu o achiziție facturabilă.

## Ce face iConta.eu

Verificat direct în cod: nu există nicio integrare între modulul de deconturi de deplasare (`core/deconturi.py` și fluxul lui din `core/uc_tenants.py`) și modulul de e-Factura/SPV al aplicației — nicio referință încrucișată între cele două, la nicio căutare exhaustivă în cod. Decontul de deplasare se înregistrează exclusiv ca notă contabilă internă (avans, cheltuială, diferență de restituit sau de plătit), independent de circuitul de facturare electronică.

Cu alte cuvinte, iConta.eu **nu leagă** astăzi decontul de deplasare de fluxul e-Factura — și, dată fiind natura diferită a celor două documente (decontul intern vs. factura de la furnizor), o asemenea legătură automată nu ar avea, oricum, o justificare fiscală directă în forma sugerată de titlu. Facturile de cazare/transport primite de la furnizori urmează circuitul obișnuit de e-Factura al aplicației, separat de ecranul „Decont deplasare / diurnă".

[iConta.eu](/)
