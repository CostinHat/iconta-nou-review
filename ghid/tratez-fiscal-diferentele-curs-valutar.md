---
title: "Cum tratez fiscal diferențele de curs valutar?"
description: "Regula generală de la impozitul pe profit pentru diferențele de curs, în lipsa unei excluderi speciale, și distincția față de regimul microîntreprinderilor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez fiscal diferențele de curs valutar?

Depinde de regimul de impozitare al firmei. La impozit pe profit, diferențele de curs urmează regula generală: pleci de la rezultatul contabil și nu ai nicio corecție specială pentru ele, deci veniturile din 765 sunt impozabile, iar cheltuielile din 665 sunt deductibile. La microîntreprinderi, regula e diferită și explicită: diferențele de curs se scad din baza impozabilă lunară, cu o regularizare separată în trimestrul IV.

## Temeiul legal

::: ghid-temei
„(1) Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. [...] Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală."
— Legea 227/2015 (Codul fiscal), art. 19 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **La impozit pe profit** (art. 19 alin. (1)): niciun articol din Codul fiscal nu exclude diferențele de curs din calculul general al rezultatului fiscal — veniturile din 765 sunt impozabile, cheltuielile din 665 sunt deductibile, exact ca orice alt venit/cheltuială financiară înregistrată contabil.
- Excepție punctuală: costurile îndatorării (dobânzi și pierderi nete din curs valutar asociate finanțării prin datorii) au un regim special de plafonare la art. 40^2 — dar acesta vizează finanțarea, nu diferențele de curs din activitatea comercială curentă.
- **La microîntreprinderi** (art. 53 alin. (1) lit. h și i): veniturile din diferențe de curs valutar se scad din baza impozabilă lunară/trimestrială — nu se impozitează cu 1%/3% în perioada curentă.
- Tot la microîntreprinderi, în trimestrul IV (sau ultimul trimestru al perioadei impozabile), diferența favorabilă netă cumulată de la începutul anului se adaugă înapoi la bază (art. 53 alin. (2) lit. b) — o regularizare anuală.

## Ce se greșește în practică

- Se aplică, din reflex, regula de la microîntreprinderi (scădere din bază) și la firmele plătitoare de impozit pe profit, unde nu există o asemenea excludere.
- Se confundă limitarea de la costurile îndatorării (art. 40^2, specifică finanțării) cu o presupusă limitare generală a deductibilității diferențelor de curs din activitatea comercială.
- Se omite, la microîntreprinderi, regularizarea din trimestrul IV, tratând diferențele de curs ca fiind complet neimpozitate pe tot parcursul anului.

## Ce face iConta.eu

Funcționalitatea de diferențe de curs valutar (`core/diferente_curs.py`, F041) e un motor pur de contabilizare pe 665/765 — calculează suma și generează nota, la decontare sau la reevaluare lunară. Aplicația **nu calculează impozitul pe profit** și **nu calculează impozitul pe veniturile microîntreprinderilor** pe baza acestor conturi: nu există în cod nicio legătură între `diferente_curs.py` și motoarele de declarații fiscale (D101, D710 sau echivalent). Regulile de mai sus rămân, deocamdată, aplicate manual de contabil, pe baza rulajului 665/765 generat automat de F041.

[iConta.eu](/)
