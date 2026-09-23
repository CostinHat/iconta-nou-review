---
title: "Cum se calculează marja comercială?"
description: "Explică formula legală a marjei profitului în regimul special TVA la marjă pentru bunuri second-hand și cum o calculează automat iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează marja comercială?

Acest ghid tratează marja profitului în sensul regimului special de TVA pentru bunuri second-hand (art. 312 Cod fiscal) — nu adaosul comercial generic folosit la stabilirea prețurilor de vânzare. Dacă vindeți bunuri folosite (achiziționate în scopul revânzării) și aplicați regimul special, aceasta e formula relevantă.

## Temeiul legal

::: ghid-temei
"persoana impozabilă revânzătoare este persoana impozabilă care, în cursul desfășurării activității economice, achiziționează sau importă bunuri second-hand [...] în scopul revânzării"
— Codul fiscal (Legea 227/2015), art. 312 alin. (1) lit. e), `anaf_surse/cod_fiscal_227_2015_consolidat.txt` (linia 19802), dosar de cercetare F098.

"marja profitului este diferența dintre prețul de vânzare aplicat de persoana impozabilă revânzătoare și prețul de cumpărare, în care: 1. prețul de vânzare constituie suma obținută de persoana impozabilă revânzătoare de la cumpărător sau de la un terț, [...] taxele și alte cheltuieli, cum ar fi cele de comision, ambalare, transport și asigurare, percepute de persoana impozabilă revânzătoare cumpărătorului [...]; 2. prețul de cumpărare reprezintă tot ce constituie suma obținută, conform definiției prețului de vânzare, de furnizor, de la persoana impozabilă revânzătoare"
— Codul fiscal (Legea 227/2015), art. 312 alin. (1) lit. g), `anaf_surse/cod_fiscal_227_2015_consolidat.txt` (linia 19802), dosar de cercetare F098.

"pentru determinarea taxei colectate aferente fiecărei livrări, din marja profitului [...] se calculează suma taxei colectate [...] prin aplicarea procedeului sutei mărite"
— HG 1/2016 (norme metodologice CF), pct. 86 alin. (4) lit. c), `anaf_surse/hg_1_2016_norme_cod_fiscal.txt` (linia 8919-8920, Titlul VII), dosar de cercetare F098.
:::

Marja profitului se calculează, pentru fiecare bun vândut, ca diferență între prețul de vânzare și prețul de cumpărare al aceluiași bun. Din această marjă (care include deja TVA-ul), taxa colectată se extrage prin procedeul sutei mărite: TVA = marja × cotă / (100 + cotă). Exemplu (cotă 21%): un bun cumpărat cu 600 lei și vândut cu 1.000 lei are marja 400 lei; TVA colectată = 400 × 21 / 121 = 69,42 lei; marja netă (fără TVA) = 330,58 lei. Dacă marja e negativă sau zero (bunul se revinde sub prețul de achiziție), nu se colectează TVA.

## Ce se greșește în practică

Greșeala frecventă e calcularea TVA-ului direct pe marjă, la cota nominală (marja × cotă / 100), fără procedeul sutei mărite — asta supraevaluează taxa colectată. A doua greșeală e aplicarea acestei formule pe un total agregat (de exemplu diferența dintre totalul vânzărilor și totalul achizițiilor pe o perioadă), în loc de calculul individual, pe fiecare bun vândut.

## Ce face iConta.eu

Motorul de calcul (`core/tva_marja.py`) aplică exact formula de mai sus, pe fiecare vânzare individuală: cota de TVA e un parametru obligatoriu (fără valoare implicită — dacă lipsește, aplicația refuză explicit calculul, ca să nu se rupă tăcut de o schimbare de cotă), iar rotunjirea se face cu regula fiscală (ROUND_HALF_UP, 2 zecimale). La marjă negativă sau zero, aplicația calculează TVA = 0, fără să colecteze taxă. Nota contabilă generată (prin ruta dedicată vânzării în regim de marjă) înregistrează separat costul, marja netă și TVA-ul aferent.

[iConta.eu](/)
