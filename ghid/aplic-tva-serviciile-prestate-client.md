---
title: Cum aplic TVA la serviciile prestate către un client din UE cu cod invalid
description: Fără cod de TVA valid al clientului din UE, serviciul B2B intracomunitar nu mai e neimpozabil în România — operațiunea devine, fiscal, o prestare către persoană fără cod valid, iar TVA-ul românesc se facturează normal.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum aplic TVA la serviciile prestate către un client din UE cu cod invalid

Regula de bază pentru serviciile B2B intracomunitare e că locul prestării e la sediul beneficiarului — operațiunea nu e impozabilă în România, iar taxa o calculează clientul, în statul lui, prin taxare inversă. Regula depinde însă de o singură condiție: clientul să aibă cod de TVA valid la data operațiunii.

## Temeiul legal

::: ghid-temei
„CF art. 278 alin. (2) — Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” — sursă: `cod_fiscal_227_2015_consolidat.txt`, L17303-17420, verificat în dosarul F050.
:::

Codul sursă al motorului F050 descrie explicit efectul lipsei codului valid: „`valideaza_prestare_ic(cod_tva_client, cod_valid_vies)` — validează serviciul B2B intracomunitar (art. 278 alin. 2): client non-RO + cod valid VIES → neimpozabil în România, se declară D390 (S); fără cod valid → B2C, se facturează cu TVA românesc (art. 278 alin. 3).” Referința la alin. (3) vine din antetul modulului `core/intracomunitar.py`; textul integral al alineatului nu a fost extras verbatim în dosarul de cercetare F050, doar numărul articolului și efectul lui, așa cum reiese din cod.

## Ce înseamnă practic

Fără cod valid, clientul e tratat, fiscal, ca un beneficiar fără calitate de persoană impozabilă înregistrată intracomunitar — regula B2B de neimpozabilitate în România nu se mai aplică. Consecința: **facturezi cu TVA românesc**, la cota aplicabilă serviciului, exact ca pentru un client intern. Operațiunea nu se mai declară în D390, pentru că nu mai e o prestare intracomunitară în sensul art. 278 alin. (2).

## Ce se greșește în practică

Cea mai frecventă greșeală e verificarea codului o singură dată, la semnarea contractului, și nu la fiecare factură — un cod valid la începutul colaborării poate deveni invalid, iar ce contează e starea la data prestării, nu la primul contact. A doua: tratarea serviciului ca „automat neimpozabil în UE” doar pentru că beneficiarul e o firmă dintr-un alt stat membru, fără verificarea condiției de fond. A treia: continuarea facturării fără TVA după ce codul a devenit invalid, descoperită abia la o notificare de neconcordanță VIES sau la un control.

## Ce face iConta.eu

La emiterea facturii pentru un client din UE, sistemul verifică automat codul de TVA în VIES. Motorul intern al operațiunilor intracomunitare validează explicit condiția serviciului B2B — cod valid al clientului — și, când lipsește, tratează operațiunea ca B2C: facturare cu TVA românesc, în loc de neimpozabilitate cu declarare D390. Nu se aplică scutire sau neimpozabilitate „din prezumție” — tratamentul urmează întotdeauna rezultatul verificării.

[iConta.eu](/)
