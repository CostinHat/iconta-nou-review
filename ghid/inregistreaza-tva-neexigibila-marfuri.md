---
title: Cum se înregistrează TVA neexigibilă la mărfuri?
description: La gestiunea la preț cu amănuntul, TVA-ul aferent adaosului nedeclarat încă (aferent vânzărilor viitoare) se ține în contul 4428, separat de TVA-ul deductibil de la achiziție (4426); se descarcă lunar, odată cu marfa vândută, pe măsura vânzărilor efective.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează TVA neexigibilă la mărfuri?

Într-o gestiune la preț cu amănuntul (metoda global-valorică), TVA-ul nu se tratează unitar — există TVA deductibilă, dedusă normal la achiziție, și TVA neexigibilă, calculată pe prețul de vânzare cu amănuntul, care devine exigibilă abia pe măsură ce marfa se vinde efectiv.

## Temeiul legal

::: ghid-temei
„Contul 371 «Mărfuri» ... în debit — «valoarea la preț de înregistrare a mărfurilor achiziționate (401, ...)»; «valoarea adaosului comercial și taxa pe valoarea adăugată neexigibilă, în situația în care evidența mărfurilor se ține la preț cu amănuntul (378, 4428)»; în credit — «valoarea la preț de înregistrare a mărfurilor ieșite din gestiune prin vânzare ... (607)»; «valoarea adaosului comercial și a taxei pe valoarea adăugată neexigibile aferente mărfurilor ieșite din gestiune (378, 4428)».”

„Contul 4428 «Taxa pe valoarea adăugată neexigibilă» (cont bifuncțional): «În acest cont se evidențiază, potrivit legii, taxa pe valoarea adăugată neexigibilă.»”

— *OMFP 1802/2014, Capitolul 16, funcțiunea conturilor 371 și 4428.*
:::

## Cum se înregistrează, pas cu pas

1. **La recepția mărfii**, pe lângă costul de achiziție (371=401) și TVA deductibilă (4426=401), se calculează TVA aferentă prețului de vânzare cu amănuntul al mărfii (cost + adaos) și se înregistrează ca TVA neexigibilă: `371 = 4428`.
2. **TVA neexigibilă rămâne „latentă”** pe soldul contului 4428 cât timp marfa nu s-a vândut — nu se declară, nu se plătește, nu apare în decontul de TVA.
3. **La vânzarea efectivă a mărfii** (descărcare de gestiune, de regulă lunară), TVA-ul aferent vânzărilor lunii devine exigibil și se descarcă din 4428, în corespondență cu 371: `4428 = 371`. Abia din acest moment TVA-ul respectiv intră în calculul TVA colectate de declarat.

## Ce se greșește în practică

- Se confundă contul 4428 (TVA neexigibilă din gestiunea la preț cu amănuntul) cu regimul de TVA la încasare, care folosește tot contul 4428, dar pentru un mecanism fiscal complet diferit (exigibilitatea legată de încasarea facturii, nu de vânzarea mărfii din gestiune) — cele două mecanisme nu trebuie amestecate pe același rulaj, altfel calculul coeficientului de adaos se denaturează.
- Se declară TVA neexigibilă direct în decontul de TVA, la momentul recepției — TVA-ul devine exigibil abia la vânzare, nu la achiziție.
- Se calculează TVA neexigibilă pe costul de achiziție, nu pe prețul de vânzare cu amănuntul (cost + adaos) — soldul contului 371 include, la preț cu amănuntul, TVA calculată pe întreaga valoare de vânzare, nu doar pe cost.

## Ce face iConta.eu

Motorul `core/stocuri.py`, funcția `nir_gv`, generează la recepție linia `371=4428` pentru TVA neexigibilă, alături de `371=401` (cost), `4426=401` (TVA deductibilă) și `371=378` (adaos) — cota de TVA e obligatorie explicit pe fiecare linie sau ca parametru, aplicația refuzând să presupună tacit o cotă implicită. La descărcarea lunară, funcția `descarcare_gv` calculează TVA aferentă vânzărilor lunii (`tva_vanzari`) proporțional din stocul curent (`tva_vanzari = rc_707 × tva_stoc / baza_stoc`, o cotă medie din stoc, cu avertisment explicit în cod că „proporțional din 4427 e riscant”) și generează nota de descărcare cu linia `4428=371`.

Atenție: `descarca_luna` citește rulajul contului 4428 **fără filtrare pe sursă** de operațiune — dacă firma folosește și ecranul separat de „TVA la încasare (art. 282)”, care produce note manuale tot pe 4428, acele mișcări se adună la cele din gestiunea global-valorică, denaturând calculul. Dacă firma combină ambele mecanisme, verificați separat sursa fiecărei mișcări pe contul 4428 înainte de a valida descărcarea lunară.

[iConta.eu](/)
