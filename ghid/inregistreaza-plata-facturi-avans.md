---
title: "Cum se înregistrează plata unei facturi în avans?"
description: "Cum contabilizează iConta.eu un avans plătit unui furnizor, cu evidențiere separată în contul 409 și TVA deductibil la data plății."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează plata unei facturi în avans?

Când plătești un furnizor înainte de livrarea bunurilor sau prestarea serviciilor, suma nu se înregistrează direct pe contul 401 „Furnizori”, ci separat, în contul 409 „Furnizori – debitori”, până la decontarea ei prin factura finală.

## Temeiul legal

::: ghid-temei
„Contul 409 «Furnizori ‐ debitori» […] Cu ajutorul acestui cont se ține evidența avansurilor acordate furnizorilor pentru cumpărări de bunuri de natura stocurilor, prestări de servicii, imobilizări corporale sau necorporale. Contul 409 «Furnizori ‐ debitori» este un cont de activ. […] Soldul contului reprezintă avansuri acordate furnizorilor, nedecontate.” — OMFP 1802/2014
:::

::: ghid-temei
„4091 Furnizori - debitori pentru cumpărări de bunuri de natura stocurilor […] 4092 Furnizori - debitori pentru prestări de servicii […] 4093 Avansuri acordate pentru imobilizări corporale […] 4094 Avansuri acordate pentru imobilizări necorporale” — OMFP 1802/2014
:::

Contul 409 se detaliază pe patru subconturi, în funcție de destinația avansului: 4091 pentru stocuri, 4092 pentru servicii, 4093 pentru imobilizări corporale, 4094 pentru imobilizări necorporale. Nota contabilă generală la plata avansului este 409x + 4426 = 401 — avansul propriu-zis pe subcontul potrivit, iar TVA-ul aferent devine deductibil odată cu plata.

## Ce se greșește în practică

Greșeala frecventă este înregistrarea avansului direct pe contul 401, împreună cu restul datoriilor față de furnizor. Așa se pierde evidența separată a sumelor nedecontate, iar la primirea facturii finale devine greu de urmărit cât s-a achitat deja în avans. O a doua greșeală este alegerea subcontului nepotrivit (de exemplu 4092 „servicii” pentru un avans dat pentru stocuri) — nu schimbă TVA-ul, dar denaturează structura avansurilor pe tipuri.

## Ce face iConta.eu

iConta.eu generează nota contabilă 409x + 4426 = 401 pentru avansul plătit, cu subcontul corespunzător destinației (4091 stocuri / 4092 servicii / 4093 imobilizări corporale / 4094 imobilizări necorporale). Cota de TVA trebuie introdusă explicit — aplicația nu presupune tacit o cotă implicită, tocmai pentru a evita riscul aplicării unei cote vechi. La sosirea facturii finale, iConta generează nota de regularizare inversă (401 = 409x, 401 = 4426). Aplicația tratează fiecare avans ca operațiune independentă; nu urmărește automat un sold cumulat al mai multor avansuri parțiale succesive pentru aceeași comandă.

[iConta.eu](/)
