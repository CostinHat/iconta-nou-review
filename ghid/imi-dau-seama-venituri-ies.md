---
title: "Cum îmi dau seama de la ce venituri ies din micro"
description: "Plafonul de venituri de 100.000 euro pentru 2026 și momentul din care o microîntreprindere trece la impozit pe profit, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum îmi dau seama de la ce venituri ies din micro

Ieșirea din regimul micro nu se întâmplă „quando se observă" la final de an, ci automat, din trimestrul în care plafonul de venituri e depășit — iar plafonul pentru 2026 e mai mic decât în anii anteriori.

## Temeiul legal

::: ghid-temei
„Pentru anul fiscal 2025/2026, limita veniturilor realizate, reprezentând echivalentul în lei a 250.000 euro, respectiv echivalentul în lei a 100.000 euro începând cu 1 ianuarie 2026, se verifică pe baza veniturilor realizate de către persoana juridică română la data de 31 decembrie 2024, respectiv la data de 31 decembrie 2025."
— Legea nr. 227/2015 (Codul fiscal), art. 54 alin. (3), coroborat cu art. 47 alin. (1) lit. c) („a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro") (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie urmărit concret în 2026:

- Plafonul de venituri pentru a rămâne micro este, începând cu 1 ianuarie 2026, de **100.000 euro** (redus față de 250.000 euro, cât era anterior) — verificat pe bază de venituri cumulate de la începutul anului fiscal.
- Dacă în cursul anului fiscal veniturile depășesc acest plafon, firma **datorează impozit pe profit** — nu de la data la care s-a constatat depășirea, ci potrivit regulilor de la art. 52, calculate pe baza limitelor verificate cumulat.
- Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la **închiderea exercițiului financiar precedent**, nu cel din ziua în care se face verificarea.
- Dacă firma este „legată" (potrivit definițiilor de la art. 47 alin. (1^1)) cu alte persoane juridice sau cu PFA-uri ale asociaților, veniturile relevante pentru plafon se **cumulează** cu veniturile acelor persoane legate — nu se verifică izolat doar cifra de afaceri proprie.

## Ce se greșește în practică

- Se verifică plafonul doar la finalul anului, deși legea cere verificarea veniturilor cumulate de la începutul anului fiscal, trimestru de trimestru, pentru a surprinde momentul exact al depășirii.
- Se aplică vechiul plafon de 250.000 euro pentru anul 2026, deși acesta a scăzut la 100.000 euro începând cu 1 ianuarie 2026.
- Se ignoră obligația de cumulare a veniturilor cu întreprinderile legate, ceea ce poate duce la depășirea reală a plafonului fără ca firma să observe, dacă privește izolat doar propriile încasări.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu verifică și nu semnalează automat** depășirea plafonului de 100.000 euro — nu există, în cod, nicio constantă a plafonului micro (confirmat explicit în comentariile din `core/control_fiscal_api.py`); regimul fiscal (`regim_fiscal`) rămâne un câmp declarat manual de contabil, la Date firmă. Verificarea cumulării cu veniturile unor întreprinderi legate externe (alte firme sau PFA-uri ale asociaților, care nu sunt gestionate în același cont iConta.eu) rămâne, firesc, în sarcina utilizatorului, pentru că aplicația nu are acces la evidențele altor entități din afara ei.

[iConta.eu](/)
