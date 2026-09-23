---
title: "Cum declar exporturile în D300: rândurile corecte"
description: Exporturile scutite cu drept de deducere se raportează în D300 pe rândul livrărilor scutite (rd.14) — dar atenție, e o regulă diferită de cea pentru importuri, unde D300 nu populează automat rândul specific la data acestei cercetări.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum declar exporturile în D300: rândurile corecte

Un export scutit cu drept de deducere nu dispare din decontul de TVA — el se raportează, ca orice altă livrare, pe rândul destinat operațiunilor scutite cu drept de deducere. Important e să nu se confunde această raportare cu cea a unei operațiuni neimpozabile sau cu regulile aplicabile importurilor din afara UE, care sunt diferite.

## Temeiul legal

::: ghid-temei
„Sunt scutite de taxă: a) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către furnizor sau de altă persoană în contul său; ... b) livrările de bunuri expediate sau transportate în afara Uniunii Europene de către cumpărătorul care nu este stabilit în România sau de altă persoană în contul său [...]”

— Codul fiscal (Legea 227/2015 consolidat), art. 294 alin. (1) lit. a)-b)
:::

Fiind o operațiune scutită **cu drept de deducere** (nu neimpozabilă și nu scutită fără drept de deducere), exportul se raportează pe rândul din D300 rezervat livrărilor scutite cu drept de deducere, nu pe un rând generic de operațiuni "neimpozabile".

## Ce se greșește în practică

- Se caută rândul de export doar după memorie, fără să se verifice dacă operațiunea a fost înregistrată corect ca livrare extracomunitară (nu ca livrare intracomunitară, care are alt regim de raportare, prin D390).
- Se presupune că, fiindcă nu poartă TVA, exportul se raportează la fel ca o operațiune neimpozabilă — de fapt scutirea cu drept de deducere e o categorie distinctă în decont.
- Se confundă regula de la export cu cea de la import: exportul (livrare) și importul (achiziție din afara UE) sunt raportate diferit în D300, iar tratamentul uneia nu se aplică automat celeilalte.

## Ce face iConta.eu

Pentru operațiunile de export extracomunitar, motorul intern rutează facturile emise către parteneri din afara UE pe rândul din D300 destinat livrărilor scutite cu drept de deducere (rd.14) — comportament confirmat direct în codul de rutare al declarației (`d300.py:319-320, 332-333`), verificat la 17.09.2026.

De precizat o limitare importantă, ca să nu se creeze confuzie la firmele care fac și import, nu doar export: la aceeași dată a cercetării, aplicația **nu populează automat** rândul de TVA la import (rd.21) pentru operațiunile de import din afara UE — acestea rămân clasificate generic pe rd.26 (neimpozabil), indiferent de modul de tratare a TVA calculat de motorul de import. Este o limitare de stare curentă a aplicației, deja cunoscută, nu o regulă fiscală nouă — dacă firma are și operațiuni de import, raportarea lor în D300 trebuie verificată manual, separat de exporturi.

[iConta.eu](/)
