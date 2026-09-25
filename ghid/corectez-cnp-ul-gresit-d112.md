---
title: "Cum corectez CNP-ul greșit în D112?"
description: "Diferența dintre a corecta CNP-ul unui salariat în evidența firmei și a corecta o declarație 112 deja depusă la ANAF — două operațiuni distincte, cu efecte diferite."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez CNP-ul greșit în D112?

Un CNP greșit introdus la un salariat se poate propaga într-o declarație 112 depusă deja la ANAF. Sunt însă două lucruri diferite: corectarea sursei (fișa salariatului, de unde pornesc toate declarațiile viitoare) și corectarea unei declarații deja transmise, care are un mecanism legal separat — declarația rectificativă.

## Temeiul legal

::: ghid-temei
„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] Declarațiile [...] pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 privind Codul de procedură fiscală, art. 105 alin. (1) și (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Legea nu permite „suprascrierea" tăcută a unei declarații deja depuse: corectarea unei declarații de impunere, cum e D112, se face exclusiv prin depunerea unei **declarații rectificative** distincte.
- Termenul în care poți corecta e legat de termenul de prescripție a dreptului organului fiscal de a stabili creanțe fiscale — nu e un termen scurt, fix, de câteva zile.
- Corectarea sursei de date (evidența internă a firmei) și depunerea declarației rectificative sunt două pași separați: primul schimbă ce se va declara în viitor, al doilea repară ce a fost deja transmis.

## Ce se greșește în practică

- Se corectează CNP-ul greșit doar în fișa salariatului din aplicația de contabilitate și se presupune că declarația 112 deja depusă la ANAF „se actualizează" automat — nu se actualizează, rămâne exact cum a fost transmisă.
- Se uită să se mai depună o declarație 112 rectificativă pentru lunile în care CNP-ul greșit a fost deja raportat, expunând firma la neconcordanțe între datele proprii și cele de la ANAF.
- Se presupune că un CNP „cu format corect" (13 cifre) e automat valid, ignorând cifra de control — o cifră de control greșită poate fi respinsă tacit la validare, fără un mesaj clar despre cauză.

## Ce face iConta.eu

Corectarea CNP-ului la nivelul evidenței interne se face din butonul **„Corectează datele"** al salariatului, în ecranul **Stat de plată** — nu într-un ecran separat „Salariați". CNP-ul introdus e validat cu același algoritm complet, cu cifră de control (mod-11), atât pe formularul din interfață cât și pe server, ca să nu ajungă în baza de date o valoare care ar fi respinsă mai târziu de validatorul oficial al declarației 112. Textul afișat chiar în acel ecran, verbatim: *„Corectarea acestor date NU modifică declarațiile deja depuse. CNP-ul se validează la salvare."* Deci, onest: **iConta.eu corectează doar sursa** pentru generările viitoare de D112 — declarația rectificativă pentru o lună deja depusă cu CNP greșit, conform art. 105 din Codul de procedură fiscală, e un proces separat, pe care această corectare de date nu îl declanșează automat.

[iConta.eu](/)
