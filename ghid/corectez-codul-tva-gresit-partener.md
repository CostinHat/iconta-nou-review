---
title: "Cum corectez codul TVA greșit al unui partener în D390?"
description: Corecția se face la sursă (factură sau linie manuală), nu prin editarea directă a codului; verificarea automată a codului acoperă doar Germania, Croația și Franța.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez codul TVA greșit al unui partener în D390?

Depinde de sursa operațiunii: dacă provine dintr-o factură din sistem, corectezi codul de TVA al partenerului la sursă (pe factură/în datele partenerului), apoi regenerezi D390; dacă e o linie introdusă manual, o ștergi și o adaugi din nou cu codul corect.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1** (coloana „Cod operator intracomunitar"):
> „[...] codul de identificare în scopuri de TVA al persoanei care achiziţionează bunurile în alt stat membru decât România [...]" — și analog, pentru fiecare tip de operațiune, codul partenerului din statul membru respectiv.
:::

Norma cere ca declarația să conțină codul de TVA corect al partenerului pentru fiecare operațiune — fără el (sau cu un cod greșit), integralitatea codurilor declarate e exact ce verifică ANAF în etapa de verificare formală, după depunere.

## Ce se greșește în practică

Greșeala tipică este să se aștepte ca aplicația să valideze automat orice cod de TVA introdus, la introducere — nu e cazul decât pentru trei state membre (vezi mai jos); pentru restul, un cod malformat trece nesemnalat până la validarea finală la depunere.

## Ce face iConta.eu

Nu există un endpoint de „actualizare" a codului unui partener direct în declarația D390 — motorul de clasificare are doar operațiuni de adăugare/ștergere pentru liniile manuale, fără editare in-place. Practic:

- dacă operațiunea greșită provine dintr-o **factură** din sistem, corectezi codul de TVA al partenerului la sursă (pe factură sau pe fișa partenerului) și regenerezi D390 — clasificarea automată preia noul cod;
- dacă e o **linie manuală**, o ștergi și adaugi una nouă, cu codul corect.

Aplicația rulează un diagnostic per-partener asupra codurilor introduse (format, lungime, țară), dar verificarea prin cifră de control (checksum) funcționează, conform codului verificat, doar pentru **Germania, Croația și Franța** — pentru restul statelor membre, codul e marcat intern „neverificat", fără niciun avertisment vizibil. Un cod malformat pentru, de exemplu, Italia sau Spania nu va fi semnalat de aplicație la introducere — eroarea iese la iveală abia la validarea finală (DUK/VIES), la depunere.

[iConta.eu](/)
