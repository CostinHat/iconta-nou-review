---
title: "Cum se verifică plafonul lunar pentru beneficiile neimpozabile?"
description: "Beneficiile extrasalariale (masă, cazare, alte avantaje) au un plafon lunar comun de 33% din salariul de bază, peste care devin impozabile — cum se verifică și ce intră în calcul."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se verifică plafonul lunar pentru beneficiile neimpozabile?

Mai multe categorii de beneficii extrasalariale — hrana, cazarea/chiria suportată de angajator, alte avantaje similare — nu sunt neimpozabile fiecare separat, la infinit, ci se încadrează împreună într-un plafon lunar unic, raportat la salariul de bază al angajatului. Ce trece de acest plafon devine venit impozabil.

## Temeiul legal

::: ghid-temei
„Următoarele venituri cumulate lunar nu reprezintă venit impozabil în înțelesul impozitului pe venit, în limita plafonului lunar de cel mult 33% din salariul de bază corespunzător locului de muncă ocupat sau din solda lunară/salariul lunar acordată/acordat potrivit legii."
— Legea nr. 227/2015 (Codul fiscal), art. 76 alin. (4^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Plafonul e de **cel mult 33% din salariul de bază** al angajatului pentru luna respectivă (nu din salariul minim pe economie, nu un plafon fix în lei).
- În acest plafon comun intră **cumulat**, lunar, mai multe categorii de beneficii — de exemplu contravaloarea hranei și cazarea/chiria suportată de angajator — fiecare cu propriile condiții de acordare, dar toate concurând la același plafon de 33%.
- Ce depășește plafonul lunar de 33% devine **venit impozabil** pentru angajat, supus impozitului pe venit și, după caz, contribuțiilor sociale, ca orice alt avantaj salarial.
- Nu toate beneficiile extrasalariale intră în acest plafon comun — unele (de exemplu tichetele culturale sau de creșă) au regim fiscal propriu, cu plafoane separate, stabilite prin alte acte normative.

## Ce se greșește în practică

- Se verifică fiecare beneficiu izolat față de propriul plafon legal (de exemplu valoarea maximă a tichetului de masă), fără să se mai verifice și suma tuturor beneficiilor din plafonul comun de 33% pentru luna respectivă.
- Se raportează plafonul de 33% la salariul minim pe economie, în loc de salariul de bază individual al fiecărui angajat.
- Se includ în plafonul de 33% beneficii care au, de fapt, regim fiscal separat (de exemplu tichetele culturale), dublând sau greșind verificarea.

## Ce face iConta.eu

La data acestui ghid, motorul de salarizare din iConta.eu (`core/salarizare.py`) tratează diferențiat tipurile de beneficii — de exemplu marchează explicit în cod că tichetele culturale „NU intră în plafonul 33%" — și modulul de beneficii (`core/beneficii_api.py`) verifică plafoane individuale pentru anumite categorii (tichet de creșă, tichet cultural, cadouri). Nu am găsit însă o funcție dedicată care să însumeze, pentru fiecare angajat și fiecare lună, toate beneficiile care concurează la plafonul comun de 33% din salariul de bază și să semnaleze depășirea — această verificare agregată rămâne, la acest moment, în sarcina contabilului.

[iConta.eu](/)
