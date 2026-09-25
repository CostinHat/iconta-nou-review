---
title: "SRL pe profit 2026: cum calculez impozitul de 16%"
description: "Formula legală de calcul a impozitului pe profit — rezultatul fiscal, nu profitul contabil — și cota unică de 16% aplicabilă în 2026."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SRL pe profit 2026: cum calculez impozitul de 16%

Impozitul pe profit nu se aplică pur și simplu asupra profitului din contabilitate — legea cere un calcul separat, al „rezultatului fiscal", care pleacă de la datele contabile dar le corectează cu venituri neimpozabile, deduceri fiscale și cheltuieli nedeductibile.

## Temeiul legal

::: ghid-temei
„Articolul 17 Cota de impozitare
Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%.
Articolul 19 Reguli generale
(1) Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. La stabilirea rezultatului fiscal se iau în calcul și elemente similare veniturilor și cheltuielilor, potrivit normelor metodologice, precum și pierderile fiscale care se recuperează în conformitate cu prevederile art. 31. Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală.
(2) Rezultatul fiscal se calculează trimestrial/anual, cumulat de la începutul anului fiscal."
— Legea 227/2015 (Codul fiscal), art. 17 și art. 19 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Formula de calcul, pas cu pas, care rezultă din text:

1. **Se pornește de la rezultatul contabil** — diferența dintre veniturile și cheltuielile înregistrate potrivit reglementărilor contabile (venituri contabile minus cheltuieli contabile).
2. **Se scad veniturile neimpozabile** (ex. anumite dividende primite, venituri din anularea unor provizioane nedeductibile) și deducerile fiscale la care firma are dreptul.
3. **Se adaugă cheltuielile nedeductibile** (ex. cheltuieli fără document justificativ, partea din protocol care depășește plafonul legal, amenzi și penalități).
4. **Rezultatul pozitiv e profit impozabil**; asupra lui se aplică cota de **16%**, obținând impozitul pe profit datorat.
5. **Calculul e cumulat, trimestrial sau anual**, de la începutul anului fiscal — nu separat pe fiecare trimestru izolat, ci cumulând veniturile și cheltuielile de la 1 ianuarie.

Important: acest calcul e complet diferit de impozitul pe veniturile microîntreprinderilor (cotă aplicată direct pe venituri, nu pe profit) — un SRL „pe profit" e cel care a optat sau a fost obligat să treacă la acest regim, de regulă pentru că nu (mai) îndeplinește condițiile cumulative ale regimului micro.

## Ce se greșește în practică

- Se aplică 16% direct pe profitul contabil, fără corecțiile fiscale obligatorii (venituri neimpozabile scăzute, cheltuieli nedeductibile adăugate) — rezultatul fiscal aproape niciodată nu coincide exact cu profitul contabil.
- Se calculează impozitul separat pe fiecare trimestru, izolat, în loc de cumulat de la începutul anului fiscal, așa cum cere art. 19 alin. (2) — asta poate distorsiona plățile anticipate trimestriale.
- Se confundă rezultatul fiscal negativ (pierdere fiscală) cu o simplă pierdere contabilă, fără să se aplice regulile de recuperare a pierderii fiscale din anii următori, prevăzute la art. 31.
- Se ignoră faptul că erorile contabile corectate pe seama rezultatului reportat cer, pentru anii fiscali la care se referă, o declarație rectificativă separată (art. 19 alin. (3) lit. a)) — nu doar o corecție tăcută în anul curent.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează impozitul pe profit prin `core/d101.py`, funcția `calcul_d101()`, reconstruită după formularul oficial D101 (OPANAF 206/2025, structura D101_A600 v10). Aplicația preia intrările contabile (P1, P2, P4, P5 — corespunzătoare rândurilor oficiale ale formularului) și calculează automat câmpurile derivate, inclusiv impozitul minim pe cifra de afaceri, atunci când e cazul (`impozit_minim_cifra_afaceri()`). Cota de 16% și structura de calcul urmează direct formularul oficial ANAF, nu o formulă simplificată proprie.

[iConta.eu](/)
