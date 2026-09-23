---
title: "Cum se raportează un furnizor persoană fizică în D406?"
description: Cum se identifică, în structura SAF-T, un furnizor persoană fizică — codul de tip 03 și CNP-ul, distinct de codul folosit pentru o firmă românească sau un operator străin.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează un furnizor persoană fizică în D406?

SAF-T cere identificarea fiecărui partener (client sau furnizor) printr-un cod care arată tipul lui — persoană juridică română, operator străin sau persoană fizică. Un furnizor persoană fizică nu se raportează cu un cod fiscal generic sau inventat, ci cu un cod distinct din nomenclatorul tehnic al schemei, urmat de CNP-ul lui.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.

Secțiunea MasterFiles cuprinde, printre subsecțiunile ei, Suppliers (furnizori) și Customers (clienți), alături de GeneralLedgerAccounts, Tax Table, UOMTable, Products, Owners și celelalte nomenclatoare ale declarației.
:::

## Cum se identifică furnizorul, în practică

Fiecare partener din MasterFiles poartă un cod de tip, urmat de identificatorul propriu-zis, conform nomenclatorului tehnic al schemei SAF-T:

- **00** + CUI — partener persoană juridică din România;
- **01** + cod fiscal — operator din Uniunea Europeană;
- **02** + cod fiscal — operator din afara Uniunii Europene;
- **03** + CNP — persoană fizică, identificată prin codul numeric personal;
- **04** + nume — partener fără cod de identificare cunoscut (excepțional).

Un furnizor persoană fizică, fără CUI de firmă, se raportează deci cu codul **03**, urmat de CNP-ul lui — nu cu un cod de firmă inventat și nu cu identificatorul lăsat gol. E o distincție structurală a schemei, nu o interpretare: dacă furnizorul nu are CUI, formatul de persoană juridică nu se forțează peste el.

## Ce se greșește în practică

- Se raportează furnizorul persoană fizică cu un cod fiscal fictiv sau cu identificatorul lăsat gol, în loc de codul 03+CNP.
- Se confundă codul 03 (persoană fizică identificată prin CNP) cu 04 (partener fără cod cunoscut) — 04 e o excepție, nu varianta implicită pentru o persoană fizică.
- Se presupune că faptul că furnizorul e persoană fizică face imposibilă raportarea lui corectă în D406 — e posibilă, cu codul potrivit din nomenclator.

## Ce face iConta.eu

iConta.eu determină automat codul de tip al fiecărui partener (00/01/02/03/04) din datele lui — CUI, CNP sau lipsa lor — nu se introduce manual pe fiecare factură. Identificarea partenerilor a fost reparată explicit în cod (anterior emisă ca identificator brut, fără prefixul de tip) și e gardată la emitere, ca să nu se poată produce un fișier fără codul corespunzător.

[iConta.eu](/)
