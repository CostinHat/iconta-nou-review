---
title: "Comisioanele bancare sunt deductibile fiscal?"
description: "Regula generală de deductibilitate a cheltuielilor la impozitul pe profit, aplicată comisioanelor bancare percepute pentru operarea conturilor firmei."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Comisioanele bancare sunt deductibile fiscal?

Comisioanele percepute de bancă pentru operarea conturilor firmei (mentenanță cont, transfer bancar, emitere card, retragere numerar la ATM pentru nevoile firmei) sunt, în principiu, cheltuieli deductibile la calculul impozitului pe profit — pentru că se încadrează direct în regula generală de deductibilitate: sunt cheltuieli efectuate în scopul desfășurării activității economice.

## Temeiul legal

::: ghid-temei
„(1) Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cheltuielile efectuate în scopul desfășurării activității economice, inclusiv cele reglementate prin acte normative în vigoare, precum și taxele de înscriere, cotizațiile și contribuțiile datorate către camerele de comerț și industrie, organizațiile patronale și organizațiile sindicale."
— Legea nr. 227/2015 privind Codul fiscal, art. 25 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din acest articol rezultă principiul aplicabil comisioanelor bancare:

- **Regula generală de deductibilitate** e legată de scopul cheltuielii — dacă un cont bancar și operațiunile aferente lui (plăți, încasări, mentenanță) servesc activității economice a firmei, comisioanele plătite băncii pentru aceste operațiuni sunt cheltuieli deductibile.
- Codul fiscal nu prevede, la verificarea la sursă, o categorie de limitare specifică sau o condiție suplimentară pentru comisioanele bancare — spre deosebire de alte tipuri de cheltuieli (de exemplu, cheltuielile de protocol sau cele cu autoturisme), care au reguli de deductibilitate limitată la articolele următoare.
- Condiția practică rămâne cea generală, valabilă pentru orice cheltuială: să existe documentul justificativ (extrasul de cont, nota de comision emisă de bancă) care să susțină înregistrarea și să confirme legătura cu activitatea economică a firmei.

## Ce se greșește în practică

- Se presupune că orice comision bancar e automat nedeductibil sau parțial deductibil, prin analogie cu alte cheltuieli limitate (protocol, sponsorizare) — Codul fiscal nu prevede o astfel de limitare specifică pentru comisioanele bancare; se aplică regula generală de la art. 25 alin. (1).
- Se înregistrează comisioanele bancare fără documentul justificativ corespunzător (extrasul de cont sau nota de comision), bazându-se doar pe suma dedusă automat din sold — orice cheltuială, inclusiv comisionul bancar, trebuie să aibă la bază documentul justificativ cerut de Legea contabilității (art. 6, Legea 82/1991).
- Se confundă comisioanele aferente unui cont folosit exclusiv în scop personal al asociatului/administratorului cu cele aferente contului firmei — doar comisioanele legate de activitatea economică a firmei intră sub regula de deductibilitate de la art. 25 alin. (1).

## Ce face iConta.eu

iConta.eu oferă evidența contabilă generală a operațiunilor bancare, inclusiv a comisioanelor reținute automat de bancă, pe baza extraselor bancare importate și procesate (`core/banca.py`, `core/banca_parser.py`). Aplicația nu are o regulă specială separată pentru comisioanele bancare — le tratează, corect, ca orice altă cheltuială înregistrată pe baza documentului justificativ (extrasul de cont), fără o limitare de deductibilitate suplimentară, în lipsa unei prevederi legale specifice care s-o impună.

[iConta.eu](/)
