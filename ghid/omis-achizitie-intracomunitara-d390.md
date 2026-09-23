---
title: "Ce fac dacă am omis o achiziție intracomunitară din D390?"
description: Achiziția omisă poate ajunge în D390 automat, prin D301, dacă are completată țara furnizorului — altfel se adaugă manual, cu atenție la dubla raportare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă am omis o achiziție intracomunitară din D390?

Depinde dacă operațiunea există deja în sistem (ca factură sau ca operațiune declarată în D301) sau nu există deloc.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1 lit. c)**:
> „[...] c) achiziţii intracomunitare de bunuri, achiziţii intracomunitare asimilate prevăzute la art. 273 alin. (2) lit. a) [...]"

**NOTA 1 (furnizor fără cod de TVA valid)**:
> „Pentru achiziţii intracomunitare de bunuri taxabile în România, în cazul în care furnizorul nu comunică un cod valabil de TVA, dar bunurile sunt transportate de pe teritoriul unui stat membru al Uniunii Europene, achiziţia se declară în declaraţia recapitulativă [...] Coloana «Tipul operaţiunii» - se va înscrie «A»."
:::

## Ce se greșește în practică

Greșeala tipică este adăugarea manuală a unei achiziții care, de fapt, există deja în sistem — ca factură sau ca operațiune deja înregistrată în D301 — ceea ce duce la dublă raportare: aplicația semnalează situația doar ca avertisment, nu blochează, iar bazele impozabile se adună în loc să se dedupliceze automat.

## Ce face iConta.eu

**Dacă achiziția e deja înregistrată în D301**, aplicația poate deriva automat operațiunea în D390 — dar doar dacă operațiunea din D301 are completată țara furnizorului. Dacă D390 iese „pe zero", dar D301 conține operațiuni fără țara furnizorului completată, aplicația afișează un mesaj explicit care îndrumă spre completarea acestei informații în D301, nu direct în D390.

**Dacă achiziția nu există în sistem sub nicio formă**, o adaugi ca linie manuală din panoul de clasificare D390 (pasul 2), cu tipul corect — A pentru bunuri, S pentru servicii. Dacă furnizorul nu a comunicat un cod de TVA valid, dar bunurile provin totuși dintr-un stat membru UE, declari operațiunea tot ca A, cu țara obligatorie și codul de operator necompletat (cazul NOTA 1, citat mai sus).

Un caz frecvent, semnalat direct în aplicație: o factură primită fără codul de TVA al furnizorului nu e preluată automat — dacă achiziția „lipsește" din D390, verifică întâi dacă nu cumva codul furnizorului lipsește pe factura/operațiunea sursă, înainte să adaugi o linie manuală suplimentară (pentru a evita dubla raportare de mai sus).

[iConta.eu](/)
