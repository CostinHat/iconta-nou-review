---
title: Cum corectez contul 4423 dacă nu corespunde cu D300?
description: Contul 4423 (TVA de plată) se compară cu soldul de la sfârșitul perioadei din D300, dar verificarea e tăcută dacă ambele valori sunt zero — utilă doar când firma chiar are TVA de plată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez contul 4423 dacă nu corespunde cu D300?

Contul **4423** (TVA de plată) se compară, pe credit, cu rândul „Sold TVA de plată la sfârșitul perioadei" din D300 (R41_2). Dacă ambele valori sunt zero, verificarea nu afișează nimic — are sens doar când firma chiar are, la finalul perioadei, o obligație de plată.

## Temeiul legal

::: ghid-temei
Art. 281 din Codul fiscal (Legea 227/2015) — "Faptul generator pentru livrări de bunuri și prestări de servicii" — stabilește momentul de la care se naște obligația de TVA. Soldul contului 4423 reflectă diferența dintre TVA colectată și dedusă, calculată din facturile lunii; balanța o reflectă doar dacă toate notele aferente sunt validate. Titlul și numărul articolului sunt confirmate în sursele legale folosite de aplicație; textul integral nu e citat literal aici.
:::

## Cum apare o divergență pe 4423

Soldul contului 4423 e, practic, rezultatul comparațiilor de pe 4427 (colectată) și 4426 (dedusă) — dacă oricare din acestea are o diferență nerezolvată (notă nevalidată, storno neînregistrat, factură înregistrată în altă lună, TVA la încasare, regularizare), soldul final de plată se resimte și el. De aceea, prima verificare utilă nu e direct pe 4423, ci pe cele două conturi din care el rezultă.

## Ce faci în funcție de cauză

- **Cauză dovedită mecanic** — o factură fără notă validată explică exact diferența: poți valida corecția propusă.
- **Cauză sugerată** — există deja o notă în ciornă care ar rezolva diferența: trebuie doar validată, nu recreată.
- **Cauză nedovedită** — note manuale directe pe 4423, storno neînregistrat, regularizări, TVA la încasare: nu se face nicio ajustare automată; e nevoie de investigație manuală înainte de a corecta soldul.

## Ce se greșește în practică

- Se ajustează manual soldul 4423 direct, fără să se identifice întâi dacă diferența vine de pe partea de colectată sau de dedusă.
- Se așteaptă un semnal chiar și când firma nu are TVA de plată în acea lună — verificarea pe 4423 e tăcută în acest caz, nu „verde" implicit.
- Se ignoră posibilitatea ca diferența să vină dintr-o notă manuală introdusă direct pe cont, nu dintr-o factură — caz în care aplicația nu poate propune o corecție automată.

## Ce face iConta.eu

Aplicația compară automat soldul creditor al contului 4423 cu rândul „Sold TVA de plată" din D300, cu o toleranță de 1 leu, și rămâne tăcută dacă ambele valori sunt zero. Când diferența e explicată mecanic de o notă nevalidată pe conturile de colectată sau dedusă, propune corecția; când cauza ține de note manuale directe pe cont, storno neînregistrat sau regularizări, semnalează diferența pentru investigație manuală, fără să modifice automat soldul.

[iConta.eu](/)
