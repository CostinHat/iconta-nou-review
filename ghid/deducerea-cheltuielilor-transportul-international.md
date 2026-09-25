---
title: "Deducerea cheltuielilor cu transportul internațional"
description: "Deductibilitatea cheltuielilor de transport și cazare pentru deplasările în interesul serviciului, distinctă de plafonul de neimpozitare a diurnei la salariat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Deducerea cheltuielilor cu transportul internațional

Cheltuielile efective de transport internațional (bilete, combustibil, taxe de drum, cazare) făcute în interesul activității economice sunt deductibile la calculul impozitului pe profit ca orice altă cheltuială legată de activitatea firmei — regula generală de deductibilitate, nu un plafon special. Diferit e regimul indemnizației/diurnei acordate salariatului aflat în deplasare, care are un plafon legal de neimpozitare în sarcina angajatului.

## Temeiul legal

::: ghid-temei
„Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cele efectuate în scopul desfășurării activității economice [...]."
— Legea 227/2015, art. 25 alin. (1), Titlul II (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„[Nu sunt venituri impozabile la salariat, în limita plafonului neimpozabil] indemnizația de delegare, indemnizația de detașare, inclusiv indemnizația specifică detașării transnaționale [...], altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare, primite de salariați [...], pe perioada desfășurării activității în altă localitate, în țară sau în străinătate, în interesul serviciului, pentru partea care depășește plafonul neimpozabil stabilit astfel: [...] (ii) în străinătate, 2,5 ori nivelul legal stabilit pentru diurnă, prin hotărâre a Guvernului, pentru personalul român trimis în străinătate pentru îndeplinirea unor misiuni cu caracter temporar, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat."
— Legea 227/2015, art. 76 alin. (2) lit. k), Titlul IV (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele două regimuri, deseori confundate, sunt independente:

- **La firmă (impozitul pe profit)** — cheltuielile efective de transport și cazare pentru deplasări în interesul serviciului, în țară sau în străinătate, sunt deductibile pe baza regulii generale de la art. 25 alin. (1): trebuie doar să fie efectuate în scopul activității economice și justificate cu documente. Codul fiscal nu prevede, în Titlul II, un plafon procentual sau valoric pentru deductibilitatea acestor cheltuieli la nivelul firmei.
- **La salariat (impozitul pe venit)** — indemnizația/diurna primită de salariatul aflat în deplasare e neimpozabilă doar până la un plafon (2,5 ori nivelul stabilit prin HG pentru personalul bugetar, în limita a 3 salarii de bază, pentru misiuni în străinătate); partea care depășește plafonul devine venit salarial impozabil pentru angajat, indiferent dacă firma o deduce sau nu.

Cu alte cuvinte: firma poate deconta și deduce integral cheltuielile reale de transport internațional, dar dacă acordă o diurnă mai mare decât plafonul legal, diferența devine impozabilă la salariat — nu la firmă.

## Ce se greșește în practică

- Se aplică plafonul de 2,5 ori nivelul HG (relevant pentru impozitul pe venit al salariatului, art. 76) și la deductibilitatea cheltuielilor de transport ale firmei, limitându-le nejustificat la calculul impozitului pe profit.
- Se confundă cheltuiala de transport propriu-zisă (biletul de avion, combustibilul, taxa de drum) cu indemnizația/diurna — doar diurna are plafon de neimpozitare la salariat; cheltuielile de transport și cazare documentate sunt, de regulă, excluse explicit din categoria supusă acelui plafon.
- Se omite justificarea documentară a deplasării (ordin de deplasare, bilete, facturi) ca temei al deductibilității, expunând cheltuiala unui risc de reclasificare la un eventual control.

## Ce face iConta.eu

iConta.eu are un motor dedicat de deconturi de deplasare și diurnă (`core/deconturi.py`), care separă automat, pe decont, cele trei componente — diurnă, transport, cazare — și calculează plafonul de neimpozitare a diurnei conform art. 76 alin. (2) lit. k) și alin. (4^1): minimul dintre 2,5 ori diurna bugetară și 3 salarii de bază raportate la zilele lucrătoare din lună, cu partea care depășește plafonul tratată ca venit salarial impozabil. Funcția acoperă și deplasările externe, cu diurna bugetară și cursul valutar introduse pentru țara respectivă (HG 518/1995), nu doar cele interne (HG 714/2018, actualizat prin Ordinul MF 1235/2023). Transportul și cazarea decontate pe bază de documente (625 = 542) rămân integral deductibile la firmă, separat de diurnă, exact distincția descrisă mai sus — contabilul introduce sumele din decont, iar aplicația face împărțirea neimpozabil/impozabil, nu invers.

[iConta.eu](/)
