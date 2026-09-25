---
title: "Ce declarații trebuie depuse după înființarea unui SRL?"
description: "Ce declarații fiscale devin obligatorii pentru un SRL nou-înființat, în funcție de vectorul fiscal ales la înregistrare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce declarații trebuie depuse după înființarea unui SRL?

După înregistrarea la Registrul Comerțului, obligațiile declarative ale unui SRL nu sunt fixe — depind de vectorul fiscal stabilit prin declarația de înregistrare fiscală: regimul de impozitare, statutul de plătitor de TVA și existența salariaților.

## Temeiul legal

::: ghid-temei
„Persoana impozabilă care are sediul activității economice în România și realizează sau intenționează să realizeze o activitate economică ce implică operațiuni taxabile, scutite de taxa pe valoarea adăugată cu drept de deducere, cu locul în România, trebuie să solicite înregistrarea în scopuri de TVA la organul fiscal competent [...]"
— Legea 227/2015 (Codul fiscal), art. 316 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce declarații devin, de regulă, obligatorii imediat după înființare:

- **D100** (declarația privind obligațiile de plată la bugetul de stat) — trimestrial pentru regimul micro (impozit pe veniturile microîntreprinderilor), anual pentru impozitul pe profit (cu plăți/declarare distincte pentru firmele plătitoare de profit).
- **D112** — lunar, din prima lună în care firma are cel puțin un salariat sau o persoană asimilată (administrator remunerat, de exemplu), pentru contribuții sociale și impozit pe venituri din salarii.
- **D300** (decontul de TVA) — lunar sau trimestrial, doar dacă firma e înregistrată în scopuri de TVA; **D390** — lunar, doar dacă firma face operațiuni intracomunitare.

## Ce se greșește în practică

- Se presupune că, fără salariați, firma nu are nicio obligație declarativă — de fapt regimul de impozit (D100) rămâne datorat indiferent de existența salariaților.
- Se depune D300 din prima lună, deși firma nu e încă înregistrată în scopuri de TVA — declarația se depune doar dacă vectorul fiscal include acest statut.
- Se ignoră faptul că regimul micro cere, pentru firmele nou-înființate, îndeplinirea condiției de a avea cel puțin un salariat în 90 de zile de la înregistrare — nerespectarea termenului schimbă regimul în impozit pe profit, cu declarații diferite.

## Ce face iConta.eu

Pe baza vectorului fiscal completat în ecranul „Date firmă" (`core/vector_fiscal_api.py`), motorul de conformare al iConta.eu (`core/control_fiscal_api.py`, funcția `declaratii_datorate`) calculează automat ce declarații sunt datorate lunar sau trimestrial pentru firma respectivă, ținând cont de regimul fiscal, statutul de plătitor de TVA, periodicitatea decontului și operațiunile intracomunitare. Aplicația nu depune însă declarația de înregistrare fiscală inițială la ANAF — aceasta e un pas separat, făcut la înființare.

[iConta.eu](/)
