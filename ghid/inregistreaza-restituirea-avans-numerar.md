---
title: "Cum se înregistrează restituirea unui avans în numerar?"
description: "Ce se întâmplă contabil cu soldul contului 409 sau 419 când un avans nu mai este decontat printr-o factură, ci restituit în numerar."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează restituirea unui avans în numerar?

Un avans acordat unui furnizor (cont 409) sau încasat de la un client (cont 419) se decontează, în mod normal, prin factura finală. Dacă operațiunea nu mai are loc — contractul se anulează, iar suma se restituie efectiv — soldul avansului trebuie stins printr-o ieșire (sau intrare) de numerar/bancă, nu prin factură.

## Temeiul legal

::: ghid-temei
„Contul 409 «Furnizori ‐ debitori» […] Contul 409 «Furnizori ‐ debitori» este un cont de activ. […] Soldul contului reprezintă avansuri acordate furnizorilor, nedecontate.” — OMFP 1802/2014
:::

Textul OMFP 1802/2014 citat mai sus descrie explicit doar decontarea avansului prin factură (creditul contului 409 se înregistrează „cu ocazia regularizării plăților” cu furnizorul, pe 401/404). Restituirea în numerar a unui avans nefolosit nu este o operațiune descrisă separat în acest text — logica generală rămâne însă aceeași: soldul contului 409 (sau 419, pentru avansurile încasate de la clienți) reprezintă o sumă nedecontată, iar la restituire acest sold trebuie stins prin contul de trezorerie care primește sau plătește efectiv banii.

## Ce se greșește în practică

Greșeala tipică: la restituirea avansului, contul 409/419 rămâne deschis (nedecontat) în evidență, sau suma e trecută direct pe venituri/cheltuieli, în loc să fie stinsă prin contul de casă sau bancă implicat.

## Ce face iConta.eu

iConta.eu automatizează, prin motorul dedicat avansurilor, doar decontarea prin factură: `nota_regularizare_avans_platit` generează inversarea 401 = 409x, 401 = 4426 atunci când sosește factura finală. Pentru restituirea efectivă în numerar a unui avans nefolosit, dosarul de cercetare al acestei funcționalități nu confirmă o funcție dedicată în aplicație — stingerea contului 409 (sau 419) prin casă/bancă rămâne o notă contabilă introdusă manual de contabil, având ca reper soldul avansului nedecontat.

[iConta.eu](/)
