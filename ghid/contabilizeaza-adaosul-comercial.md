---
title: Cum se contabilizează adaosul comercial?
description: Rolul contului 378 și notele contabile prin care adaosul comercial intră și iese din gestiunea global-valorică, în iConta.eu.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează adaosul comercial?

Adaosul comercial (marja comerciantului), la metoda prețului cu amănuntul, nu se ține evidențiat pe fiecare articol în parte, ci printr-un cont rectificativ distinct — contul 378 — care ajustează valoarea de înregistrare a mărfurilor din contul 371.

## Temeiul legal

::: ghid-temei
„Cu ajutorul acestui cont se ține evidența adaosului comercial (marja comerciantului) aferent mărfurilor din unitățile comerciale."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), secțiunea Plan de conturi, funcțiunea contului 378 „Diferențe de preț la mărfuri"
:::

::: ghid-temei
„Soldul contului reprezintă valoarea adaosului comercial aferent mărfurilor existente în stoc la sfârșitul perioadei."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), secțiunea Plan de conturi, funcțiunea contului 378 „Diferențe de preț la mărfuri"
:::

::: ghid-temei
Contul 371 „Mărfuri" (cont de activ): în debit — „valoarea la preț de înregistrare a mărfurilor achiziționate (401, ...)"; „valoarea adaosului comercial și taxa pe valoarea adăugată neexigibilă, în situația în care evidența mărfurilor se ține la preț cu amănuntul (378, 4428)"; în credit — „valoarea la preț de înregistrare a mărfurilor ieșite din gestiune prin vânzare ... (607)"; „valoarea adaosului comercial și a taxei pe valoarea adăugată neexigibile aferente mărfurilor ieșite din gestiune (378, 4428)".
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), secțiunea Plan de conturi, funcțiunea contului 371 „Mărfuri"
:::

Contul 378 este un cont rectificativ: în credit se înregistrează adaosul aferent mărfurilor care intră în gestiune, iar în debit adaosul aferent mărfurilor care ies din gestiune. Soldul lui, la un moment dat, arată exact adaosul comercial aferent mărfurilor rămase în stoc.

## Cum se contabilizează, în două momente

**La intrarea mărfii în gestiune (recepție/NIR):** adaosul comercial stabilit pentru articolele recepționate se înregistrează prin nota `371 = 378` — mărfurile intră în contul 371 la prețul de vânzare (cost de achiziție plus adaos), iar adaosul aferent se evidențiază separat, în creditul contului 378.

**La descărcarea lunară de gestiune (vânzare):** adaosul aferent mărfurilor vândute în lună, calculat prin coeficientul K aplicat la valoarea vânzărilor, se scoate din stoc prin nota `378 = 371`, alături de costul mărfii vândute (`607 = 371`) și de TVA neexigibilă aferentă (`4428 = 371`). Formula de calcul a adaosului descărcat este:

```
adaos descărcat = K × valoarea vânzărilor lunii (contul 707)
```

## Ce se greșește în practică

- Se înregistrează adaosul la intrare direct în contul 607, fără să treacă prin 378 — pierzându-se astfel evidența separată a adaosului comercial aferent stocului rămas.
- Se descarcă adaosul lunar fără să se fi calculat corect coeficientul K, ceea ce duce la o valoare descărcată în 378 care nu corespunde adaosului real aferent vânzărilor lunii.

## Ce face iConta.eu

La fiecare recepție (NIR) global-valorică, aplicația propune automat nota de adaos `371 = 378`, alături de notele de cost de achiziție și TVA deductibilă. La descărcarea lunară, adaosul aferent vânzărilor se calculează automat prin coeficientul K și se propune ca notă de ciornă `378 = 371`, împreună cu costul mărfii vândute și TVA neexigibilă aferentă — contabilul validează manual înainte ca notele să devină definitive.

[iConta.eu](/)
