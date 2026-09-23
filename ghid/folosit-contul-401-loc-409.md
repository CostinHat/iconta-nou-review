---
title: "Ce fac dacă am folosit contul 401 în loc de 409?"
description: Un avans plătit unui furnizor înregistrat greșit pe contul obișnuit de furnizori (401) în loc de avans (409x) se corectează manual, prin stornare și reînregistrare — nu există o funcție automată de reclasare între cele două conturi.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac dacă am folosit contul 401 în loc de 409?

Contul 401 (Furnizori) și contul 409 (Furnizori - debitori) au roluri diferite: 401 e datoria firmei față de furnizor pentru bunuri/servicii deja primite, în timp ce 409 e o creanță a firmei — un avans plătit furnizorului, înainte de livrare. Confuzia între ele denaturează evidența.

## Temeiul legal

::: ghid-temei
„Contul 409 «Furnizori - debitori» [...] Cu ajutorul acestui cont se ține evidența avansurilor acordate furnizorilor pentru cumpărări de bunuri de natura stocurilor, prestări de servicii, imobilizări corporale sau necorporale. Contul 409 «Furnizori - debitori» este un cont de activ." — OMFP nr. 1802/2014 pentru aprobarea reglementărilor contabile
:::

Fiind de activ, 409 arată o creanță a firmei (bani dați în avans, de recuperat prin livrarea viitoare) — opusul contului 401, care e o datorie a firmei.

## Ce faci concret

Mecanismul de avansuri are patru operații fixe: avans plătit, regularizare avans plătit, avans încasat, regularizare avans încasat — **nicio operație de corecție/reclasare** a unei sume deja înregistrate greșit. Dacă un avans plătit unui furnizor a fost trecut din greșeală pe 401 (ca și cum ar fi o factură primită) în loc de 409 (avans), corectarea se face manual:

1. Se stornează nota greșită de pe 401.
2. Se reînregistrează suma corect, ca avans plătit, folosind subcontul potrivit din grupa 409 — 4091 (stocuri), 4092 (servicii), 4093 (imobilizări corporale) sau 4094 (imobilizări necorporale), în funcție de natura achiziției pentru care s-a plătit avansul.

## Ce se greșește în practică

- Se lasă avansul înregistrat pe 401, considerând că „diferența nu contează atât timp cât suma e corectă" — folosirea contului greșit denaturează atât soldul furnizorilor (401), cât și evidența avansurilor acordate (409), cu impact asupra rapoartelor financiare.
- Se caută în aplicație o funcție automată de „reclasare" între conturi — o asemenea funcție nu a fost identificată; corectarea rămâne manuală, prin stornare.
- Se alege subcontul greșit din grupa 409 (de exemplu 4092 - servicii, în loc de 4091 - stocuri) fără să se verifice natura reală a achiziției pentru care s-a plătit avansul.

## Ce face iConta.eu

Mecanismul de avansuri din iConta.eu nu are o funcție de reclasare automată a unei sume deja înregistrate pe contul greșit — corectarea unei erori de tipul 401 în loc de 409 rămâne o procedură manuală: stornarea notei greșite, urmată de reînregistrarea corectă ca avans plătit, cu subcontul potrivit din nomenclatorul 4091–4094 folosit de mecanismul de avansuri.

[iConta.eu](/)
