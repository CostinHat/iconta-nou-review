---
title: "Ce fac dacă am omis o factură din D390?"
description: Dacă declarația nu a fost încă depusă, regenerarea o corectează automat; dacă a fost deja depusă, corectarea presupune o declarație rectificativă pe care aplicația nu o generează încă automat.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă am omis o factură din D390?

Ce poți face depinde de momentul în care descoperi omisiunea: înainte de a trimite declarația la ANAF, sau după.

## Temeiul legal

::: ghid-temei
**OPANAF 705/2020, Anexa 2, Secțiunea I**:
> „Declaraţia depusă iniţial se rectifică prin depunerea unei noi declaraţii, pe acelaşi format, bifând căsuţa corespunzătoare de pe formular. În declaraţia rectificativă se rectifică tranzacţii declarate în orice perioadă de raportare anterioară şi se completează toate rubricile formularului cu datele valabile la momentul declarării, indiferent dacă acestea au mai fost declarate.
> ATENŢIE: Informaţiile completate eronat în perioade de raportare anterioare nu se corectează prin înscrierea cifrei «0» la rubrica «Bază impozabilă» [...] Se completează câte o declaraţie rectificativă pentru fiecare perioadă de raportare pentru care se operează rectificări."
:::

## Ce se greșește în practică

Greșeala tipică este să se adauge manual o operațiune ca linie separată în D390, deși factura omisă există deja în sistem și ar urma să fie preluată automat la regenerare — riscul este dubla raportare, cu baza impozabilă însumată de două ori, pentru că aplicația semnalează această situație doar ca avertisment, nu o blochează.

## Ce face iConta.eu

**Dacă declarația e la pasul 2, nedepusă încă**: la fiecare regenerare, aplicația re-citește toate facturile intracomunitare emise/primite din perioadă. Dacă factura omisă există deja în sistem (a fost introdusă, dar poate a fost emisă/înregistrată după prima generare a declarației), apăsarea butonului „Regenerează D390" o aduce automat în clasificare, fără nicio intervenție manuală suplimentară. Dacă factura pur și simplu nu există în sistem, adaugi o linie manuală (tip A/P/S/T/R, după caz) din panoul de clasificare.

**Dacă declarația a fost deja depusă**: aici trebuie să fim direcți. Legea prevede corectarea printr-o declarație rectificativă distinctă, cu o căsuță specifică bifată pe formular, pentru perioada respectivă. La acest moment, motorul D390 din aplicație emite mereu fișierul XML cu marcajul de „declarație inițială" — nu există încă un parametru care să seteze marcajul de „declarație rectificativă" conform cerinței legale citate mai sus. Aplicația poate regenera declarația cu factura omisă inclusă, dar depunerea acelei declarații nu poartă, la acest moment, marcajul de rectificativă cerut de normă. Recomandăm verificarea situației curente a acestei funcționalități în aplicație înainte de a te baza pe ea pentru o corecție post-depunere.

[iConta.eu](/)
