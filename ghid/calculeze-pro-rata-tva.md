---
title: "Cine trebuie să calculeze pro-rata TVA?"
description: "Condiția care obligă o persoană impozabilă să aplice pro-rata la deducerea TVA — realizarea simultană de operațiuni cu și fără drept de deducere — și termenul de comunicare a pro-ratei provizorii către ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cine trebuie să calculeze pro-rata TVA?

Pro-rata de TVA nu se aplică oricărei firme înregistrate în scopuri de TVA, ci doar celor care desfășoară, simultan, atât operațiuni cu drept de deducere, cât și operațiuni fără drept de deducere, și care nu pot (sau nu vor să) țină evidențe separate pentru cele două categorii.

## Temeiul legal

::: ghid-temei
„Dreptul de deducere a taxei deductibile aferente achizițiilor efectuate de către o persoană impozabilă cu regim mixt sau de către o persoană parțial impozabilă se determină conform prezentului articol. [...] Dacă persoana parțial impozabilă desfășoară activități în calitate de persoană impozabilă, din care rezultă atât operațiuni cu drept de deducere, cât și operațiuni fără drept de deducere, este considerată persoană impozabilă mixtă pentru respectivele activități și aplică prevederile prezentului articol. Persoana parțial impozabilă poate aplica pro rata în situația în care nu poate ține evidențe separate pentru activitatea desfășurată în calitate de persoană impozabilă și pentru activitatea pentru care nu are calitatea de persoană impozabilă."
— Legea nr. 227/2015 (Codul fiscal), art. 300 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cine intră, deci, sub obligația pro-rata:

- **Persoana impozabilă cu regim mixt** — firma care are, în același timp, operațiuni taxabile/scutite cu drept de deducere și operațiuni scutite fără drept de deducere (de exemplu, o firmă care prestează atât servicii taxabile, cât și servicii financiare scutite fără drept de deducere).
- Firma trebuie să comunice organului fiscal, **până la data de 25 ianuarie inclusiv**, pro-rata provizorie pe care o va aplica în anul respectiv, precum și modul de determinare a acesteia.
- Firmele care fac achiziții **destinate exclusiv** operațiunilor cu drept de deducere sau exclusiv celor fără drept de deducere nu aplică deloc pro-rata pentru acele achiziții — taxa se deduce integral, respectiv nu se deduce deloc; pro-rata se aplică doar taxei pentru care destinația nu poate fi stabilită direct.

## Ce se greșește în practică

- Se aplică pro-rata la întreaga taxă deductibilă a firmei, inclusiv la achiziții a căror destinație (operațiune cu sau fără drept de deducere) este cunoscută cu certitudine — deși legea cere aplicarea pro-rata doar acolo unde destinația nu se poate determina direct.
- Se omite comunicarea către organul fiscal, până la 25 ianuarie, a pro-ratei provizorii și a modului ei de determinare, expunând firma la riscul respingerii deducerii la un control ulterior.
- Se confundă persoana impozabilă cu regim mixt (are atât operațiuni taxabile, cât și scutite fără drept de deducere) cu persoana parțial impozabilă (desfășoară și activități în afara sferei TVA) — cele două noțiuni sunt distincte, deși ambele conduc la aplicarea pro-rata.

## Ce face iConta.eu

La data acestui ghid, în modulul de decont TVA (`core/d300.py`), iConta.eu permite introducerea manuală a unui procent de pro-rata în profilul firmei, folosit apoi la calculul ajustării taxei deduse (rândul de regularizare aferent). Aplicația **nu calculează automat** pro-rata definitivă sau provizorie pe baza operațiunilor efectiv înregistrate — determinarea procentului, comunicarea lui către organul fiscal și regularizarea anuală rămân în sarcina contabilului.

[iConta.eu](/)
