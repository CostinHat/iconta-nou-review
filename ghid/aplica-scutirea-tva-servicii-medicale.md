---
title: "Cum se aplică scutirea de TVA pentru servicii medicale"
description: "Scutirea de TVA fără drept de deducere pentru spitalizare, îngrijiri medicale și operațiuni strâns legate de acestea, desfășurate de unități autorizate, potrivit art. 292 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se aplică scutirea de TVA pentru servicii medicale

Serviciile medicale beneficiază de o scutire de TVA de interes general, dar aplicarea ei corectă depinde de două condiții cumulative din text: tipul operațiunii (spitalizare, îngrijiri medicale sau operațiuni strâns legate) și autorizarea unității care le prestează.

## Temeiul legal

::: ghid-temei
„spitalizarea, îngrijirile medicale și operațiunile strâns legate de acestea, desfășurate de unități autorizate pentru astfel de activități, indiferent de forma de organizare, precum: spitale, sanatorii, centre de sănătate rurale sau urbane, dispensare, cabinete și laboratoare medicale, centre de îngrijire medicală și de diagnostic, baze de tratament și recuperare, stații de salvare și alte unități autorizate să desfășoare astfel de activități."
— Legea nr. 227/2015 (Codul fiscal), art. 292 alin. (1) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text pentru aplicarea corectă a scutirii:

- Scutirea acoperă **spitalizarea, îngrijirile medicale și operațiunile strâns legate de acestea** — nu orice serviciu prestat de o unitate medicală este automat scutit, ci trebuie să se încadreze în această sferă.
- Condiția de **autorizare** a unității prestatoare este explicită — un cabinet sau laborator medical neautorizat pentru activitatea respectivă nu poate aplica scutirea doar pe baza obiectului de activitate declarat.
- Este o scutire **fără drept de deducere** (specifică art. 292, „Scutiri pentru anumite activități de interes general"), ceea ce înseamnă că TVA-ul aferent achizițiilor legate de aceste servicii nu se deduce.

## Ce se greșește în practică

- Se aplică scutirea pentru toate veniturile unei clinici, inclusiv pentru servicii conexe fără caracter medical (de exemplu, chirie de spații, vânzare de produse) care nu se încadrează în „îngrijiri medicale sau operațiuni strâns legate".
- Se ignoră condiția de autorizare — o activitate medicală prestată fără autorizația corespunzătoare nu beneficiază automat de scutire doar pentru că e „medicală" ca natură.
- Se deduce TVA-ul de pe achizițiile aferente serviciilor scutite, deși art. 292 prevede scutire **fără** drept de deducere.

## Ce face iConta.eu

Verificat în cod: `core/cote_tva.py` și modulele de gestiune a cotelor TVA permit configurarea operațiunilor scutite pe firmă, dar iConta.eu nu are, la acest moment, o listă automată de validare a codurilor CAEN/autorizărilor care condiționează aplicarea scutirii pentru servicii medicale potrivit art. 292 — încadrarea corectă a unei operațiuni ca scutită rămâne o decizie a contabilului, aplicația doar reflectând tratamentul TVA ales.

[iConta.eu](/)
