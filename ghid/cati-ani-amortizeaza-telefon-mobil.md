---
title: "În câți ani se amortizează un telefon mobil?"
description: "Durata normală de funcționare pentru un telefon mobil ca mijloc fix, conform Catalogului privind clasificarea și duratele normale de funcționare a mijloacelor fixe."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# În câți ani se amortizează un telefon mobil?

Dacă un telefon mobil trece pragul valoric de mijloc fix (5.000 lei din 2026), durata lui de amortizare nu se alege liber — se caută în Catalogul oficial al mijloacelor fixe, care dă un interval de ani, nu o cifră fixă.

## Temeiul legal

::: ghid-temei
„2.1.22.6.4. - receptoare telefonie mobilă. 2-4"
— HG 2139/2004 (Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe), Grupa 2, subgrupa 2.1, clasa 2.1.22 „Mașini, utilaje și instalații pentru transporturi și telecomunicații", subclasa 2.1.22.6 „Mașini, aparate și instalații pentru radio, televiziune și telecomunicații prin sateliți, telefonie mobilă" (sursă: anaf_surse/hg_2139_2004_catalog_clasificare_durate_mijloace_fixe.txt)
:::

Ce rezultă din catalog:

- Pentru un **receptor de telefonie mobilă** (categoria cea mai apropiată de un telefon mobil obișnuit), durata normală de funcționare e un interval de **2 până la 4 ani** — nu o singură cifră.
- Firma **alege** durata concretă în interiorul acestui interval, la punerea în funcțiune a mijlocului fix — odată aleasă, durata rămâne neschimbată până la recuperarea integrală a valorii sau scoaterea din uz (regula generală de utilizare a catalogului, cap. I pct. 4).
- Catalogul are și o categorie vecină, „aparate de telecomunicații pentru birou" (telefoane fixe, faxuri), cu durată **3-5 ani** — diferită de cea a telefoniei mobile; alegerea categoriei corecte contează pentru intervalul aplicabil.

## Ce se greșește în practică

- Se aplică o durată „standard" de 3 ani fără verificarea catalogului, sau se copiază durata folosită pentru alt tip de echipament IT (calculatoare, imprimante), care are propriile clase și intervale.
- Se schimbă durata aleasă pe parcursul amortizării, pentru a optimiza rezultatul fiscal — odată stabilită la punerea în funcțiune, durata rămâne fixă.
- Se confundă clasa „receptoare telefonie mobilă" (2-4 ani) cu „aparate de telecomunicații pentru birou" (3-5 ani) — sunt clase diferite în catalog, cu intervale diferite.

## Ce face iConta.eu

Pentru un mijloc fix înregistrat în aplicație, durata normală de utilizare e un câmp introdus de contabil la fișa activului — aplicația nu are un catalog al claselor de mijloace fixe din HG 2139/2004 încorporat, care să sugereze automat intervalul de ani pe tipul de bun. Odată introdusă durata, motorul de amortizare (`core/d406_active.py`) calculează corect amortizarea pe metoda aleasă (liniară, degresivă sau accelerată, în funcție de categoria de cont a activului), pornind din luna următoare punerii în funcțiune — dar alegerea intervalului de ani, conform catalogului, rămâne responsabilitatea contabilului.

[iConta.eu](/)
