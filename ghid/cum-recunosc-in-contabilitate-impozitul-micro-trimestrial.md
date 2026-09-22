---
title: Cum recunosc în contabilitate impozitul micro trimestrial?
description: Impozitul pe veniturile microîntreprinderilor se recunoaște ca o cheltuială a trimestrului în care se calculează, pe baza acelorași venituri (facturat, nu încasat) folosite pentru determinarea sumei din D100.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum recunosc în contabilitate impozitul micro trimestrial?

Impozitul micro nu este un impozit „de sfârșit de an" — el se calculează și se recunoaște contabil trimestrial, în pas cu obligația de declarare prin D100. Ghidul explică principiul de recunoaștere și legătura directă cu baza de calcul folosită pentru declarație.

## Temeiul legal

::: ghid-temei
**CF art. 51 alin. (1):**
> „Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.html`

**CF art. 53 alin. (1):**
> „Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie **veniturile din orice
> sursă**, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile
> aferente costurilor serviciilor în curs de execuție; ... j) valoarea reducerilor comerciale acordate
> ulterior facturării, înregistrate în contul «709»..."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:6480-6519`
:::

## Principiul de recunoaștere

Pentru că baza impozabilă (art. 53 alin. 1) se formează la momentul înregistrării venitului, nu la încasare, cheltuiala cu impozitul micro trebuie recunoscută în același trimestru în care venitul respectiv a fost înregistrat — nu la momentul plății efective a impozitului către bugetul de stat. Suma de recunoscut este exact cea calculată conform formulei legale: venituri trimestru × 1%.

Practic, la finalul fiecărui trimestru, după ce se stabilește baza de calcul (aceeași bază folosită pentru generarea D100), se înregistrează cheltuiala cu impozitul aferentă trimestrului respectiv, chiar dacă plata efectivă la buget se face ulterior, până la termenul de scadență al declarației.

## Ce se greșește în practică

- Se recunoaște cheltuiala cu impozitul o singură dată, la sfârșitul anului, în loc de trimestrial — distorsionează rezultatul fiecărui trimestru în parte.
- Se recunoaște cheltuiala la data plății efective către buget, nu la data la care a fost calculată obligația trimestrului.
- Se calculează suma de recunoscut pe o bază diferită de cea folosită pentru D100 (de exemplu, pe încasări), rezultând o diferență între evidența contabilă și declarația depusă.
- Se uită recunoașterea pentru un trimestru în care venitul a fost mic sau nul, deși impozitul (chiar și zero) trebuie totuși reflectat corect pentru consistența rulajelor.

## Ce face iConta.eu

`d100.pull()` determină baza impozabilă a trimestrului direct din înregistrările contabile ale firmei (conturile 70x/75x/76x minus 709), iar `deriva_obligatii` aplică cota de 1% pentru a obține suma obligației cod 121. Aceeași sumă, calculată pe aceeași bază de venituri ale trimestrului, este cea care trebuie recunoscută drept cheltuială cu impozitul micro — asigurând consistența între ce arată evidența contabilă și ce declară D100.

[iConta.eu](/)
