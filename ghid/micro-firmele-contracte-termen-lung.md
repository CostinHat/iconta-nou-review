---
title: "Micro pentru firmele cu contracte pe termen lung"
description: "Cum tratează impozitul micro veniturile aferente costurilor serviciilor/producției în curs de execuție, specifice firmelor cu contracte pe termen lung."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Micro pentru firmele cu contracte pe termen lung

Firmele cu contracte pe termen lung (construcții, dezvoltare software pe proiect, servicii care se execută pe parcursul mai multor luni) au un tratament special la impozitul micro pentru veniturile recunoscute contabil înainte de facturarea efectivă — legea le exclude explicit din baza impozabilă, ca să nu se plătească impozit pe o venitura care nu s-a materializat încă printr-o factură sau o livrare.

## Temeiul legal

::: ghid-temei
„Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile aferente costurilor serviciilor în curs de execuție; c) veniturile din producția de imobilizări corporale și necorporale; [...]."
— Legea 227/2015, art. 53 alin. (1) lit. a)-c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Veniturile aferente costurilor serviciilor în curs de execuție (contul 712, aferent unui contract pe termen lung nefinalizat la data raportării) și veniturile aferente costurilor stocurilor de produse (contul 711) sunt venituri strict contabile, generate de închiderea de lună/trimestru pentru a reflecta stadiul de execuție al unui contract — nu reprezintă o încasare sau o creanță certă către client. Legea le exclude din baza impozabilă a microîntreprinderii tocmai pentru că nu sunt „venituri" în sensul economic, ci ajustări interne ale contabilității de angajamente.

## Ce se greșește în practică

- Se impozitează cu 1% toate veniturile din balanță, inclusiv contul 711/712, deși art. 53 alin. (1) lit. a)-b) le scade explicit din baza de calcul.
- Se confundă „venituri în curs de execuție" (contul 71x, tehnic, tranzitoriu) cu facturile de avans emise pe un contract pe termen lung, care rămân, de regulă, venituri impozabile de îndată ce sunt facturate.
- Se verifică plafonul de 100.000 euro folosind și veniturile din grupa 71, deși acestea, ca și grupa 72, nu fac parte din cifra de afaceri netă (grupa 70) folosită la determinarea plafonului conform art. 47 alin. (1^1).

## Ce face iConta.eu

iConta.eu calculează baza impozitului micro din veniturile din orice sursă înregistrate strict în conturile 70x, 75x și 76x, cu scăderea reducerilor comerciale (709) — motorul de calcul (A8) exclude deliberat grupa 71x din sumă (venituri aferente costurilor stocurilor/serviciilor în curs de execuție, conturile 711/712), tocmai pentru că art. 53 alin. (1) lit. a)-b) le scade din baza impozabilă a microîntreprinderii. Dacă firma folosește aceste conturi pentru contracte pe termen lung, baza impozitului micro calculată de aplicație le exclude deja automat.

[iConta.eu](/)
