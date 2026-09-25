---
title: "TVA de recuperat: cerere de rambursare în 2026"
description: "Cum se solicită rambursarea soldului sumei negative de TVA în 2026, pragul de 5.000 lei și diferența față de reportarea în decontul următor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA de recuperat: cerere de rambursare în 2026

Când TVA dedusă într-o lună depășește TVA colectată, rezultă o sumă negativă de taxă. Firma nu e obligată să ceară banii înapoi imediat — poate opta între a solicita rambursarea sau a reporta soldul în decontul lunii următoare. Legea pune însă o limită sub care rambursarea nu poate fi cerută.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile, înregistrate conform art. 316, pot solicita rambursarea soldului sumei negative a taxei din perioada fiscală de raportare, prin bifarea casetei corespunzătoare din decontul de taxă din perioada fiscală de raportare, decontul fiind și cerere de rambursare, sau pot reporta soldul sumei negative în decontul perioadei fiscale următoare. Dacă persoana impozabilă solicită rambursarea soldului sumei negative, acesta nu se reportează în perioada fiscală următoare. Nu poate fi solicitată rambursarea soldului sumei negative a taxei din perioada fiscală de raportare, mai mic de 5.000 lei inclusiv, acesta fiind reportat obligatoriu în decontul perioadei fiscale următoare."
— Legea nr. 227/2015, art. 303 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Persoanele impozabile pot renunța la cererea de rambursare pe baza unei notificări depuse la autoritățile fiscale, urmând să preia soldul sumei negative solicitat la rambursare în decontul aferent perioadei fiscale următoare depunerii notificării."
— Legea nr. 227/2015, art. 303 alin. (8) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă mecanismul complet:

- Decontul de TVA (D300) **este el însuși** cererea de rambursare, dacă se bifează caseta corespunzătoare — nu e nevoie de o cerere separată.
- Rambursarea nu poate fi cerută dacă soldul sumei negative e de **cel mult 5.000 lei** — acesta se reportează obligatoriu în decontul următor.
- Odată solicitată rambursarea, suma nu se mai reportează; dar firma poate renunța ulterior la cerere, printr-o notificare, și să preia soldul în decontul de după depunerea notificării (art. 303 alin. (8)).

## Ce se greșește în practică

- Se depune o cerere separată de rambursare la ANAF, deși legea prevede că decontul de TVA, cu caseta bifată, este el însuși cererea de rambursare.
- Se solicită rambursarea unui sold sub 5.000 lei, deși art. 303 alin. (7) interzice explicit acest lucru sub prag — soldul rămâne reportat automat.
- Se pierde din vedere reportul cumulat — dacă rambursarea nu e cerută, soldul sumei negative din luna curentă se adună la soldul reportat din luna precedentă, conform art. 303 alin. (3), nu pornește de la zero.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează **D300** (decontul de TVA) pe baza facturilor emise și primite introduse în aplicație, calculând soldul de plată sau soldul sumei negative al perioadei, inclusiv câmpurile pentru soldul reportat din perioada precedentă. Aplicația nu decide automat dacă acest sold trebuie solicitat spre rambursare sau reportat — bifarea casetei de rambursare pe formular și evaluarea oportunității (inclusiv pragul de 5.000 lei) rămân o decizie a utilizatorului sau a contabilului.

[iConta.eu](/)
