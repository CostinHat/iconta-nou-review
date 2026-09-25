---
title: "Manual intern de proceduri de casierie 2026"
description: "Ce reguli obligatorii de disciplină financiară trebuie să conțină un manual intern de casierie în 2026, pe baza Legii 70/2015 și a monografiilor OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Manual intern de proceduri de casierie 2026

Un manual intern de casierie nu e un formular ANAF, ci un document de organizare internă prin care firma traduce în proceduri proprii plafoanele și interdicțiile din Legea 70/2015. Fără el, aceleași reguli există oricum în lege — dar responsabilitatea aplicării lor corecte, zi de zi, la ghișeul de casă, rămâne needucată.

## Temeiul legal

::: ghid-temei
„Articolul 1
(1) Operațiunile de încasări și plăți efectuate de persoane juridice, persoane fizice autorizate, întreprinderi individuale, întreprinderi familiale, liber profesioniști, persoane fizice care desfășoară activități în mod independent, asocieri și alte entități cu sau fără personalitate juridică de la/către oricare dintre aceste categorii de persoane se vor realiza numai prin instrumente de plată fără numerar, definite potrivit legii.
(3) Prevederile prezentului capitol se aplică și operațiunilor de încasări și plăți în valută efectuate pe teritoriul României. Încadrarea în plafoanele prevăzute de prezentul capitol se efectuează în funcție de cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunilor de încasări sau plăți."
— Legea 70/2015, art. 1 alin. (1) și (3) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Un manual intern serios de casierie pentru 2026 trebuie să acopere cel puțin:

- **Plafoanele de încasare/plată în numerar** (art. 3-4): 5.000 lei/zi de la o persoană juridică, 10.000 lei/zi la magazinele cash and carry, 5.000 lei/zi pentru avansuri spre decontare — cu interdicția explicită a fragmentării plăților/încasărilor pentru a evita plafonul.
- **Regula pentru fiecare casierie**, dacă firma are mai multe puncte de lucru: plafoanele se aplică **pe fiecare casierie în parte** (art. 7), nu global pe firmă.
- **Restituirile către clienți** (art. 9): plafoane separate pentru facturi stornate către alte firme (5.000/10.000 lei) și pentru retururi de la persoane fizice (10.000 lei, cu excepția celor fără cont bancar).
- **Aplicarea plafoanelor și în valută**: operațiunile în euro sau altă monedă intră sub aceleași plafoane, la cursul BNR din ziua operațiunii — un manual care tratează valuta ca „în afara legii" e greșit de la premisă.
- **Monografiile contabile de bază** pentru numerar, avansuri de trezorerie și decontări (OMFP 1802/2014).

## Ce se greșește în practică

- Se scrie un manual generic, copiat, care nu menționează explicit aplicarea plafoanelor și în valută (art. 1 alin. (3)) — o omisiune frecventă, mai ales la firmele care fac plăți ocazionale în euro.
- Se stabilesc plafoane interne mai permisive decât cele legale, „pentru fluiditate", ignorând că interdicția de fragmentare din lege se aplică indiferent de politica internă a firmei.
- Manualul nu diferențiază plafonul pe casierie de plafonul pe firmă la societățile cu mai multe puncte de lucru, ceea ce duce la aplicarea greșită a limitei la firme cu casierii multiple.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu generează un manual intern de proceduri** — acesta rămâne un document de politică internă, redactat de firmă. Aplicația are însă motorul real de casierie descris în `core/casa.py`, cu plafoanele curente din Legea 70/2015 (actualizate cu Legea 239/2025, în vigoare de la 1 ianuarie 2026) și cu verificarea lor pe fiecare operațiune introdusă, prin `core/casa_api.py` (`verifica_plafon`). Contabilul primește astfel un semnal concret când o operațiune introdusă depășește plafonul legal, dar redactarea manualului de proceduri în sine rămâne în afara aplicației.

[iConta.eu](/)
