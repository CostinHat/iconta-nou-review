---
title: "Avansurile facturate intră în plafonul micro?"
description: "Avansurile încasate sau facturate de la clienți nu se înregistrează contabil ca venit, deci nu intră, la momentul facturării, în plafonul de venituri al regimului micro."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Avansurile facturate intră în plafonul micro?

Nu, atâta timp cât avansul rămâne avans — adică nu a fost urmat de livrarea bunului sau prestarea serviciului. Contabil, un avans încasat de la un client nu e un venit, ci o datorie a firmei față de client, până la momentul în care obligația contractuală e îndeplinită.

## Temeiul legal

::: ghid-temei
„Contul 419 «Clienți - creditori» Cu ajutorul acestui cont se ține evidența clienților - creditori, reprezentând avansurile încasate de la clienți. Contul 419 «Clienți - creditori» este un cont de pasiv."
— OMFP 1802/2014, funcțiunea conturilor, grupa 41 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Coroborat cu regula de calcul a plafonului micro, aceasta arată de ce avansurile nu se cumulează în plafon:

::: ghid-temei
„c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. [...]"
— Legea 227/2015 (Codul fiscal), art. 47 alin. (1) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă, concret, pentru plafonul micro:

- Plafonul de 100.000 euro se verifică pe **veniturile realizate**, adică pe cifra de afaceri recunoscută contabil — iar un avans, contabil, este o datorie (cont 419), nu un venit.
- Venitul se recunoaște abia la livrarea bunului sau prestarea serviciului, moment în care avansul se regularizează (se stinge din 419) și se înregistrează venitul efectiv.
- O factură de avans emisă la finalul anului, dar nefollowed de livrare, nu majorează cifra de afaceri a anului respectiv — dar dacă livrarea are loc ulterior, venitul (și, implicit, impactul asupra plafonului) apare atunci.

## Ce se greșește în practică

- Se consideră toate facturile emise, inclusiv cele de avans, drept venituri ale perioadei — de fapt doar facturile de livrare/prestare efectivă generează venit contabil.
- Se ignoră TVA la exigibilitate pentru avansuri — deși avansul nu e venit contabil, TVA poate deveni exigibilă la încasarea avansului, ceea ce e o obligație distinctă de recunoașterea venitului.
- Se amână emiterea facturii finale de livrare la nesfârșit, ținând suma „în avans" artificial, tocmai ca să nu apară ca venit — practică riscantă, pentru că nu reflectă realitatea economică a tranzacției și poate fi recalificată la control.

## Ce face iConta.eu

Modulul de facturare al iConta.eu distinge tipul facturii (avans vs. factură de livrare/prestare), iar modulul de avansuri (`core/avansuri.py`) generează notele contabile corecte pentru avansul încasat/plătit și pentru regularizarea lui ulterioară (cont 419 la încasare, apoi stornare la livrare). Calculul obligațiilor pentru regimul micro (`core/d100.py`) se face pe baza veniturilor introduse de utilizator pentru trimestrul respectiv; aplicația nu recalculează însă automat, din facturile emise, care sume reprezintă venit recunoscut și care rămân avansuri nedecontate — această distincție rămâne, la acest moment, în responsabilitatea contabilului la introducerea datelor.

[iConta.eu](/)
