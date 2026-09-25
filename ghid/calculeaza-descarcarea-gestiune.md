---
title: "Cum se calculează descărcarea de gestiune?"
description: "Formula coeficientului de adaos și descărcarea lunară a gestiunii la metoda global-valorică, potrivit OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează descărcarea de gestiune?

Comercianții care țin evidența mărfurilor la preț de vânzare cu amănuntul (metoda global-valorică) nu descarcă gestiunea marfă cu marfă, ci lunar, printr-un coeficient de repartizare a adaosului comercial calculat pe baza soldurilor și rulajelor conturilor de marfă, adaos și TVA neexigibilă.

## Temeiul legal

::: ghid-temei
„Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient [...]. La calcularea procentului mediu de adaos comercial, soldul inițial al contului de mărfuri și valoarea intrărilor de mărfuri nu vor include TVA neexigibilă. Acest coeficient se înmulțește cu valoarea bunurilor ieșite din gestiune la preț de înregistrare, iar suma rezultată se înregistrează în conturile corespunzătoare în care au fost înregistrate bunurile ieșite. [...] În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare [...]. În această situație, costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor."
— OMFP 1802/2014, reglementări contabile, pct. 286 alin. (4), nota *2) și alin. (8) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Practic, calculul are doi pași:

- **Coeficientul de repartizare (K)**, cumulat de la începutul exercițiului financiar, se obține împărțind adaosul comercial (soldul inițial + rulaj creditor al contului 378) la valoarea mărfurilor la preț de vânzare minus TVA neexigibilă (contul 371 minus contul 4428) — fără TVA neexigibilă, așa cum precizează explicit nota de la pct. 286.
- **Descărcarea lunii** se face aplicând K la veniturile din vânzarea mărfurilor (contul 707, fără TVA): adaosul descărcat = K × 707, iar costul mărfii vândute (607) = 707 − adaosul descărcat.

Dacă numitorul formulei (valoarea mărfurilor la preț de vânzare minus TVA neexigibilă) e zero sau negativ, descărcarea de gestiune nu se poate calcula — de regulă e semn că soldurile conturilor 371 și 4428 nu sunt corecte la data raportării.

## Ce se greșește în practică

- Se calculează K doar pe luna curentă, nu cumulat de la începutul exercițiului — formula OMFP 1802/2014 cere valorile cumulate, nu pe perioadă izolată.
- Se descarcă gestiunea și în lunile fără vânzări de mărfuri (707 = 0), deși în acest caz nu există ce adaos să se repartizeze — descărcarea rămâne zero, nu se forțează un calcul.
- Se ignoră faptul că un coeficient K supraunitar (mai mare decât 1) indică, de regulă, o eroare în soldurile conturilor 371/378/4428, nu un adaos real de peste 100%.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **calculează efectiv descărcarea lunară de gestiune** pentru metoda global-valorică: aplicația determină coeficientul K din rulajele reale, validate, ale conturilor 371, 378 și 4428, generează nota contabilă % = 371 (607 / 378 / 4428) și semnalează explicit situațiile în care calculul nu poate fi făcut (de exemplu, când nu există vânzări de mărfuri în luna respectivă sau când soldurile conturilor nu permit un rezultat coerent).

[iConta.eu](/)
