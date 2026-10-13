---
title: "Cum se calculează marja comercială?"
description: "Explică formula legală a marjei profitului în regimul special TVA la marjă pentru bunuri second-hand și cum o calculează automat iConta.eu."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum se calculează marja comercială?

Acest ghid tratează marja profitului în sensul regimului special de TVA pentru bunuri second-hand (art. 312 Cod fiscal) — nu adaosul comercial generic folosit la stabilirea prețurilor de vânzare. Dacă vindeți bunuri folosite (achiziționate în scopul revânzării) și aplicați regimul special, aceasta e formula relevantă.

Marja profitului se calculează, pentru fiecare bun vândut, ca diferență între prețul de vânzare și prețul de cumpărare al aceluiași bun. Din această marjă (care include deja TVA-ul), taxa colectată se extrage prin procedeul sutei mărite: TVA = marja × cotă / (100 + cotă). Exemplu (cotă 21%): un bun cumpărat cu 600 lei și vândut cu 1.000 lei are marja 400 lei; TVA colectată = 400 × 21 / 121 = 69,42 lei; marja netă (fără TVA) = 330,58 lei. Dacă marja e negativă sau zero (bunul se revinde sub prețul de achiziție), nu se colectează TVA.

## Ce se greșește în practică

Greșeala frecventă e calcularea TVA-ului direct pe marjă, la cota nominală (marja × cotă / 100), fără procedeul sutei mărite — asta supraevaluează taxa colectată. A doua greșeală e aplicarea acestei formule pe un total agregat (de exemplu diferența dintre totalul vânzărilor și totalul achizițiilor pe o perioadă), în loc de calculul individual, pe fiecare bun vândut.

## Ce face iConta.eu

Motorul de calcul aplică exact formula de mai sus, pe fiecare vânzare individuală: cota de TVA e un parametru obligatoriu (fără valoare implicită — dacă lipsește, aplicația refuză explicit calculul, ca să nu se rupă tăcut de o schimbare de cotă), iar rotunjirea se face cu regula fiscală (ROUND_HALF_UP, 2 zecimale). La marjă negativă sau zero, aplicația calculează TVA = 0, fără să colecteze taxă. Nota contabilă generată (prin ruta dedicată vânzării în regim de marjă) înregistrează separat costul, marja netă și TVA-ul aferent.

[iConta.eu](/)
