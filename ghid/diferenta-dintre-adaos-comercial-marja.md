---
title: "Care este diferența dintre adaos comercial și marjă comercială?"
description: "Adaosul comercial folosit la evidența mărfurilor la preț de vânzare cu amănuntul și marja profitului din regimul special de TVA sunt două concepte diferite, cu regimuri diferite."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este diferența dintre adaos comercial și marjă comercială?

Cele două expresii se folosesc adesea interschimbabil în vorbirea curentă, dar denumesc lucruri diferite din punct de vedere contabil și fiscal. „Adaosul comercial" e o tehnică de evidență a mărfurilor la prețul de vânzare cu amănuntul, fără temei legal expres sub acest nume — e o practică de contabilitate de gestiune. „Marja profitului" (uneori numită impropriu „marjă comercială") e, în schimb, un termen **definit expres în Codul fiscal**, cu efecte directe asupra bazei de calcul a TVA, în cadrul regimului special pentru bunuri second-hand, opere de artă, obiecte de colecție și antichități.

## Temeiul legal

::: ghid-temei
„g) marja profitului este diferența dintre prețul de vânzare aplicat de persoana impozabilă revânzătoare și prețul de cumpărare, în care: 1. prețul de vânzare constituie suma obținută de persoana impozabilă revânzătoare de la cumpărător sau de la un terț, inclusiv subvențiile direct legate de această tranzacție, impozitele, obligațiile de plată, taxele și alte cheltuieli, cum ar fi cele de comision, ambalare, transport și asigurare, percepute de persoana impozabilă revânzătoare cumpărătorului, cu excepția reducerilor de preț; 2. prețul de cumpărare reprezintă tot ce constituie suma obținută, conform definiției prețului de vânzare, de furnizor, de la persoana impozabilă revânzătoare;"
— Codul fiscal (Legea 227/2015), art. 312 alin. (1) lit. g) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Diferența practică:

- **Marja profitului** (art. 312 CF) e strict definită de lege, se calculează pentru fiecare operațiune de revânzare de bunuri second-hand și devine, pentru vânzător, **baza de impozitare a TVA** — nu TVA se aplică la prețul de vânzare întreg, ci doar la această diferență (preț de vânzare minus preț de cumpărare).
- **Adaosul comercial** e diferența dintre prețul de vânzare cu amănuntul și costul de achiziție al mărfii, folosită de comercianți pentru a-și stabili prețurile și pentru evidența contabilă a stocurilor la preț de vânzare (contul 378 „Diferențe de preț la mărfuri" din planul de conturi, alături de contul 4428 pentru TVA neexigibilă). Nu are un temei legal expres sub denumirea „adaos comercial" — e o convenție de practică contabilă, nu un regim special de TVA.

Confuzia apare fiindcă ambele privesc, la bază, „diferența dintre preț de vânzare și preț de cumpărare" — dar una e o regulă fiscală specială cu domeniu de aplicare restrâns (bunuri second-hand, opere de artă, obiecte de colecție, antichități), iar cealaltă e o metodă de evidență generală a mărfurilor.

## Ce se greșește în practică

- Se aplică regimul special de marjă (art. 312) la orice marfă vândută cu adaos, indiferent de natura ei — regimul e limitat expres la bunurile second-hand, opere de artă, obiecte de colecție și antichități, nu la mărfuri obișnuite.
- Se confundă adaosul comercial (o tehnică de gestiune a stocurilor, cont 378) cu marja profitului din regimul special de TVA (o bază de impozitare legală, per operațiune).
- Se calculează TVA pe prețul integral de vânzare pentru o operațiune care ar fi trebuit taxată doar pe marjă, sau invers.

## Ce face iConta.eu

iConta.eu implementează strict conceptul legal de „marjă a profitului" din art. 312 CF, pentru operațiunile de vânzare în regim special (second-hand și, echivalent, turism — art. 311), prin motorul de calcul al regimului de marjă și raportul de citire aferent, „Jurnal regim marjă". Acest mecanism e distinct de evidența mărfurilor la preț de vânzare cu amănuntul: pentru aceasta din urmă, aplicația are un modul separat, „gestiunea global-valorică" (`core/stocuri.py`, metoda prețului cu amănuntul, OMFP 1802/2014), care calculează adaosul comercial pe articolele NIR-ului, îl contabilizează pe contul 378 („Diferențe de preț la mărfuri", cu TVA neexigibilă pe 4428) și îl descarcă lunar proporțional cu vânzările — mecanism disponibil doar firmelor care țin gestiunea în acest regim, nu celor cu gestiune cantitativ-valorică. Cele două funcționalități rămân separate în aplicație: marja profitului (art. 312) nu se calculează prin motorul de adaos comercial, și invers.

[iConta.eu](/)
