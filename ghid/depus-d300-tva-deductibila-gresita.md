---
title: Am depus D300 cu TVA deductibilă greșită
description: Controlul D390 ↔ D300 verifică doar rândurile de operațiuni intracomunitare — o eroare pe TVA deductibilă nu trece prin el și se corectează prin rectificativă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Am depus D300 cu TVA deductibilă greșită

Dacă ai depus deja un D300 cu o sumă greșită la TVA deductibilă, merită clarificat de la început: controlul încrucișat D390 ↔ D300 din aplicație nu ar fi prins acest tip de eroare, oricât de atent l-ai fi urmărit — el nu se uită la rândurile de TVA deductibilă.

## Temeiul legal

::: ghid-temei
Structura oficială a formularului D300 confirmă rândurile de comparație folosite de controlul încrucișat D390 ↔ D300: **R1_1** (livrări intracomunitare de bunuri) și **R5_1** (achiziții intracomunitare de bunuri, taxă colectată prin taxare inversă). Rândurile de TVA deductibilă din decont nu fac parte din această comparație.

Evidența contabilă folosită de aplicație pentru verificările D390 se limitează la notele contabile cu statusul „validată" (conform reglementărilor contabile, OMFP 1802/2014), legate de facturile intracomunitare — nu la rulajul integral al conturilor de TVA.
:::

Controlul încrucișat D390 ↔ D300, așa cum funcționează în aplicație, compară exact două perechi de rânduri: livrările intracomunitare de bunuri din D390 cu rândul **R1_1**, și achizițiile intracomunitare de bunuri cu rândul **R5_1** (taxă colectată prin taxare inversă). O eroare pe TVA deductibilă — de exemplu o factură de achiziție internă dedusă cu cotă greșită, sau o deducere aplicată pe o factură care nu avea drept de deducere — nu atinge niciunul dintre aceste două rânduri și nu ar fi fost semnalată de acest control.

Corectarea unei declarații deja depuse, indiferent de rândul afectat, se face prin **declarație rectificativă** — mecanismul de depunere pentru corecția unei declarații fiscale deja transmise, separat de generarea declarației inițiale.

## Ce se greșește în practică

- Se așteaptă ca un semnal verde pe controlul D390 ↔ D300 să confirme corectitudinea întregului decont, inclusiv a TVA deductibile — verdele confirmă doar coerența pe cele două rânduri intracomunitare, nu pe restul declarației.
- Se amână corecția sperând că o verificare automată o va semnala ulterior — pentru TVA deductibilă greșită, nu există un astfel de semnal în acest control; corecția trebuie inițiată de tine, prin rectificativă.
- Se confundă eroarea de deducere cu o diferență D390-D300 și se caută cauza în operațiunile intracomunitare, deși problema e pe alt rând al decontului.

## Ce face iConta.eu

Pentru operațiunile intracomunitare de bunuri, aplicația verifică automat doar rândurile R1_1 și R5_1 din D300 față de D390 și față de evidența contabilă validată — nu acoperă TVA deductibilă în general și nu are un mecanism separat care să detecteze o deducere greșită deja depusă.

Corecția unei sume greșite pe TVA deductibilă, odată depus decontul, se face prin declarație rectificativă — un pas manual, pe care tu îl inițiezi, nu o funcționalitate acoperită de controlul încrucișat descris aici.

[iConta.eu](/)
