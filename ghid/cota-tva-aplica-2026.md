---
title: Ce cotă de TVA se aplică în 2026?
description: În 2026 sunt în vigoare două cote de TVA — 21% standard și 11% redusă unică — valabile fără schimbare pe tot anul, de la 01.08.2025. Vezi regula generală și lista limitativă a excepțiilor.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce cotă de TVA se aplică în 2026?

De la 1 august 2025, sistemul de TVA din România are doar două cote pentru operațiuni impozabile: 21% standard și 11% redusă. Cotele de 5% și 9% care existau anterior au fost abrogate, iar în tot cursul lui 2026 nu a intervenit nicio altă modificare a acestor procente.

## Temeiul legal

::: ghid-temei
„Cota standard se aplică asupra bazei de impozitare pentru operațiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%. [...] Cota redusă de 11% se aplică asupra bazei de impozitare [...]” — Codul fiscal, art. 291 alin. (1)-(2), astfel cum a fost modificat de Legea nr. 141/2025 (MO nr. 699/25.07.2025), cu efect de la 1 august 2025.
:::

## Regula generală

- **21% — cotă standard**: se aplică implicit oricărei livrări de bunuri sau prestări de servicii care nu se regăsește explicit în lista de la cota redusă.
- **11% — cotă redusă unică**: se aplică doar operațiunilor enumerate limitativ la art. 291 alin. (2) lit. a)-n) — o listă închisă, nu una orientativă. Dacă o operațiune nu apare pe listă, rămâne la 21%, oricât de „firească” ar părea reducerea.
- Pentru o firmă **neplătitoare de TVA** nu se aplică nicio cotă — nu se colectează TVA deloc pe facturile emise, indiferent de natura bunului sau serviciului.

Pentru anul 2026, OUG 8/2026 a modificat alte praguri fiscale (plafonul TVA la încasare, plafonul mijlocului fix), dar nu a atins art. 291 și nu a schimbat cotele de TVA — 21%/11% rămân valabile neschimbate pe tot anul.

## Ce se greșește în practică

- Se presupune că orice produs „de bază" (alimentar, cultural, social) intră automat la 11% — lista de la alin. (2) e limitativă, nu una de principiu.
- Se aplică vechile cote 5% sau 9%, rămase din obișnuință dintr-o perioadă anterioară lui august 2025.
- Se ignoră excepțiile care scot anumite produse din categoria redusă chiar dacă par să se încadreze (băuturi alcoolice, anumite băuturi nealcoolice, alimente cu zahăr adăugat).

## Ce face iConta.eu

Cotele curente (`COTA_STANDARD = 21`, `COTA_REDUSA = 11`) sunt sursa unică internă (`core/cote_tva.py`) folosită de motorul de potrivire cotă↔produs. În paralel, `core/common.py` ține un registru „period-aware" al valorilor istorice (19% până la 31.07.2025, cote istorice 9%/5%) — astfel încât aplicația validează automat cota corectă în funcție de data operațiunii, nu doar de valoarea numerică introdusă.

[iConta.eu](/)
