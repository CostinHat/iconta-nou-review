---
title: "Cum verific D101 cu registrul de evidență fiscală?"
description: "Obligația legală de a evidenția în registrul de evidență fiscală veniturile impozabile și cheltuielile deductibile care stau la baza rezultatului fiscal raportat prin D101."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific D101 cu registrul de evidență fiscală?

Declarația 101 (impozitul pe profit) nu se completează direct din balanța contabilă — legea impune un instrument intermediar, registrul de evidență fiscală, în care se consemnează exact veniturile și cheltuielile care fundamentează rezultatul fiscal declarat.

## Temeiul legal

::: ghid-temei
„(7) În scopul determinării rezultatului fiscal, contribuabilii sunt obligați să evidențieze în registrul de evidență fiscală veniturile impozabile înregistrate într-un an fiscal, potrivit alin. (1), precum și cheltuielile efectuate în scopul desfășurării activității economice, în același an fiscal, inclusiv cele reglementate prin acte normative în vigoare, potrivit art. 25."
— Legea nr. 227/2015 (Codul fiscal), art. 19 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă acest temei pentru verificarea D101:

- Registrul de evidență fiscală trebuie să conțină **veniturile impozabile** și **cheltuielile deductibile** ale anului fiscal — o verificare corectă a D101 pornește de la a confrunta sumele din declarație cu totalurile din acest registru, nu direct cu rulajele conturilor de venituri/cheltuieli din contabilitate.
- Diferențele dintre baza contabilă (clasele 6/7 din balanță) și baza fiscală (registrul de evidență fiscală) apar tocmai din ajustările fiscale — venituri neimpozabile, cheltuieli nedeductibile, deduceri suplimentare — care nu sunt vizibile direct în conturile contabile.
- Registrul de evidență fiscală este, alături de jurnalele de vânzări/cumpărări, unul dintre documentele pe care Codul de procedură fiscală le definește explicit ca „evidențe fiscale" (art. 108 alin. (3) din același cod).

## Ce se greșește în practică

- Se compară direct suma din D101 cu rulajul conturilor de venituri și cheltuieli din balanță, ignorând că unele elemente sunt tratate diferit fiscal față de contabil (de exemplu, cheltuieli nedeductibile parțial).
- Se ține registrul de evidență fiscală retroactiv, la momentul depunerii declarației, în loc să fie actualizat pe parcursul anului fiscal, odată cu fiecare operațiune relevantă.
- Se omite reflectarea în registru a elementelor reglementate expres de acte normative (de exemplu, deduceri suplimentare pentru cheltuieli de cercetare-dezvoltare), care nu apar altfel în contabilitate ca linie separată.

## Ce face iConta.eu

Verificat în cod: `core/d101_reconciliere.py` recalculează independent, direct din balanța contabilă (`inregistrari_linii`), baza contabilă a rezultatului (veniturile și cheltuielile de exploatare și financiare) și o confruntă cu ce a produs generatorul declarației D101, semnalând orice divergență — conform docstringului modulului, acest mecanism acoperă baza **contabilă**, nu ajustările fiscale ulterioare (deduceri, cheltuieli nedeductibile), care rămân intrări manuale ale contabilului; aplicația nu are, la acest moment, un „registru de evidență fiscală" separat, generat automat, potrivit art. 19 alin. (7).

[iConta.eu](/)
