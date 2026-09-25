---
title: "Înființare SRL cu doi asociați: documente necesare"
description: "Ce trebuie să cuprindă actul constitutiv al unui SRL cu doi asociați și care e capitalul social minim, conform Legii 31/1990."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Înființare SRL cu doi asociați: documente necesare

Pentru un SRL cu doi asociați, documentul central e actul constitutiv, iar conținutul lui minim e stabilit expres de lege — nu e „la alegerea" fondatorilor. La el se adaugă cererea de înmatriculare la registrul comerțului, depusă în termen legal, și dovada capitalului social vărsat.

## Temeiul legal

::: ghid-temei
„Actul constitutiv al societății în nume colectiv, în comandită simplă sau cu răspundere limitată va cuprinde:
a) datele de identificare a asociaților [...];
b) forma, denumirea și sediul social;
c) obiectul de activitate al societății, cu precizarea domeniului și a activității principale;
d) capitalul social subscris, cu menționarea aportului fiecărui asociat, în numerar sau în natură, valoarea aportului în natură, modul evaluării acestuia; la societățile cu răspundere limitată se vor preciza numărul și valoarea nominală a părților sociale, precum și numărul părților sociale atribuite fiecărui asociat pentru aportul său [...]"
— Legea 31/1990, art. 7 lit. a)-d) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- **Termenul de înmatriculare**: „În termen de 15 zile de la data încheierii actului constitutiv, fondatorii, primii administratori [...] vor cere înmatricularea societății în registrul comerțului în a cărui rază teritorială își va avea sediul societatea" — Legea 31/1990, art. 36 alin. (1).
- **Data de la care societatea există ca persoană juridică**: „Societatea este persoană juridică de la data înmatriculării în registrul comerțului" — Legea 31/1990, art. 41 alin. (1).
- **Capitalul social minim pentru un SRL nou-înființat** a fost schimbat de la 200 lei la o sumă mai mare: „În cazul societăților cu răspundere limitată nou-înființate, valoarea minimă a capitalului social este de 500 lei" — Legea 239/2025, art. VI alin. (2), care modifică art. 11 din Legea 31/1990.
- La un SRL cu doi asociați se precizează, pentru fiecare, aportul (numerar sau natură) și numărul de părți sociale atribuite, conform art. 7 lit. d) de mai sus.

## Ce se greșește în practică

- Se pornește de la valoarea mai veche, mai mică, a capitalului social minim, fără să se verifice pragul actualizat de 500 lei pentru societățile nou-înființate, introdus de Legea 239/2025.
- Se depune cererea de înmatriculare după termenul de 15 zile de la încheierea actului constitutiv, expunând fondatorii la răspundere solidară pentru prejudiciul cauzat prin întârziere.
- Se scrie în actul constitutiv o cotă de participare fără corespondent exact în numărul și valoarea nominală a părților sociale atribuite fiecărui asociat, ceea ce creează ambiguitate ulterioară la repartizarea dividendelor sau la cesiunea părților sociale.

## Ce face iConta.eu

Din verificarea codului sursă (`FUNCTIONALITATI.csv` și modulele din `core/`), iConta.eu **nu are nicio funcționalitate pentru înființarea sau înmatricularea unei societăți**. Aplicația intervine abia după ce firma există deja în registrul comerțului: F007 (`core/asociati_import_api.py`) importă lista de asociați dintr-un fișier .xlsx/.csv, la migrarea unei firme deja înființate în aplicație, fără nicio legătură cu depunerea actului constitutiv sau cu cererea de înmatriculare. Documentele de înființare de mai sus se pregătesc și se depun la registrul comerțului prin mijloace din afara iConta.eu.

[iConta.eu](/)
