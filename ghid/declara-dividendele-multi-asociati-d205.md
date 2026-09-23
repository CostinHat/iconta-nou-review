---
title: "Cum se declară dividendele pentru mai mulți asociați în D205?"
description: "Cum împarte D205 dividendul brut între mai mulți asociați și ce validări se aplică fiecărui beneficiar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară dividendele pentru mai mulți asociați în D205?

Când o firmă are mai mulți asociați, dividendul distribuit/plătit trebuie împărțit corect între ei în D205, fiecare apărând ca beneficiar separat, cu baza și impozitul aferente cotei sale.

## Temeiul legal

::: ghid-temei
Câmpuri cheie pentru dividende (tip_venit1="08"): `divid_D` (7.V. dividende distribuite, rând 39.a), `divid_P` (8.V. dividende plătite, rând 39.b), `baza1`, `imp1`, `Rezid` (obligatoriu "1" pentru tip_venit1=08), `cifR` (CNP/NIF, obligatoriu).
— Structura XML oficială D205, `anaf_surse/d205_struct_anaf.txt` (temei: OPANAF 102/2025 și OPANAF 179/2022)
:::

Fiecare asociat apare ca beneficiar distinct în declarație, identificat prin CNP, cu propria bază de impozitare și propriul impozit calculat — nu se depune o singură sumă globală pe firmă.

## Ce se greșește în practică

Se încearcă uneori declararea unei singure sume agregate pe firmă, fără defalcare pe fiecare asociat, sau se omit asociați cu cote mici, considerându-le nesemnificative.

## Ce face iConta.eu

Repository-ul de date al D205 (`core/repo_d205.py`, funcția `select_asociati`) citește automat toți asociații cu cotă mai mare de zero și, pornind de la sumele înregistrate în contul 457 (doar din note contabile cu status "validata"), calculează pentru fiecare în parte baza și impozitul, în funcție de suma efectiv plătită acelui asociat. CUI-ul plătitorului și CNP-ul fiecărui beneficiar sunt validate pe cifră de control (checksum), nu doar verificate ca fiind completate, iar un CNP duplicat pentru același tip de venit este blocat explicit la generare. Suma totală de control din antetul declarației (`totalPlata_A`) este calculată o singură dată, la nivelul tuturor beneficiarilor, și doar preluată în XML-ul final — nu recalculată separat, pentru a evita neconcordanțe.

[iConta.eu](/)
