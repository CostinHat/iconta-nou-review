---
title: "Cum înregistrez numerarul depus din casierie în contul bancar?"
description: "Depunerea numerarului din casieria firmei în contul bancar este singura operațiune de plăți-încasări scutită de plafoanele Legii 70/2015 — ce spune legea și cum se reflectă corect în contabilitate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum înregistrez numerarul depus din casierie în contul bancar?

Plafoanele stricte pentru încasări și plăți în numerar impuse de Legea 70/2015 nasc o întrebare frecventă: se aplică vreun plafon și la depunerea numerarului din casieria firmei în contul bancar? Răspunsul din lege e clar.

## Temeiul legal

::: ghid-temei
„Plafoanele-limită prevăzute de prezentul capitol nu se aplică de către persoanele prevăzute la art. 1 alin. (1), pentru următoarele operațiuni: a) depunerea de numerar în conturile deschise la instituțiile de credit sau la instituțiile care prestează servicii de plată și care sunt autorizate de Banca Națională a României, inclusiv în automatele de încasări în numerar."
— Legea nr. 70/2015, art. 5 lit. a) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce înseamnă asta pentru operațiunea de zi cu zi:

- **Depunerea de numerar din casierie în contul bancar al firmei nu e supusă niciunui plafon** — nu contează valoarea sumei depuse, se poate depune integral soldul casei într-o singură operațiune.
- Plafoanele de 5.000 lei / 10.000 lei se aplică încasărilor și plăților în numerar între firmă și terți (clienți, furnizori), nu mișcărilor interne dintre casierie și bancă.
- Din punct de vedere contabil, operațiunea se înregistrează simplu, prin nota contabilă 581 „Viramente interne" (sau direct 5121 = 5311, în funcție de politica firmei), pe baza foii de vărsământ/chitanței de la bancă și a registrului de casă.

## Ce se greșește în practică

- Se fragmentează depunerile de numerar în tranșe mici din teama de a nu depăși un „plafon" care, de fapt, nu există pentru această operațiune.
- Se confundă plafonul de încasări/plăți către terți (5.000 lei/10.000 lei) cu o presupusă limită pentru depunerile bancare proprii ale firmei.
- Se omite corelarea sumei depuse cu soldul din registrul de casă la data operațiunii, ceea ce generează diferențe greu de justificat ulterior la un control.

## Ce face iConta.eu

iConta.eu calculează soldul rulant al registrului de casă (modulul de casierie) pe baza operațiunilor de încasare/plată introduse, cu plafoanele Legii 70/2015 aplicate corect distinct pe categorii (încasări/plăți către persoane juridice, persoane fizice, cash and carry). Depunerea numerarului din casierie în contul bancar se înregistrează ca operațiune de casă și de bancă, fără a fi supusă vreunui plafon de numerar. Aplicația are un modul de import al extraselor bancare (`core/banca_parser.py`, formate XLS/XLSX/CSV și MT940), care ajută la corelarea automată a operațiunii de depunere cu încasarea din extrasul bancar — dar potrivirea finală cu suma din foaia de vărsământ/registrul de casă rămâne verificată de utilizator.

[iConta.eu](/)
