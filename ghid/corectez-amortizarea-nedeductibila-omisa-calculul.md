---
title: "Cum corectez amortizarea nedeductibilă omisă din calculul impozitului pe profit?"
description: "Explică mecanismul add-back al amortizării contabile și limitele aplicației la corectarea unui mijloc fix deja calculat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez amortizarea nedeductibilă omisă din calculul impozitului pe profit?

## Temeiul legal

::: ghid-temei
CF art.28 alin.(2) lit.b), actualizat prin OUG 8/2026 (MO 147/25.02.2026, aplicabil de la anul fiscal 2026): plafonul de la care un mijloc fix e amortizabil este de 5.000 lei.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/obiecte_inventar.py` (funcția `prag_mf`, care citește pragul dintr-un registru de cote, cu 5.000 lei valabil din 25.02.2026), dosar de cercetare F027.

CF art.28 alin.(5): reglementează și metodele de amortizare degresivă/accelerată, alături de cea liniară.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

Amortizarea contabilă nedeductibilă se adaugă înapoi la baza impozabilă prin rândurile de tip P2x/P28, care intră în rollup-ul P34 „cheltuieli nedeductibile” din D101, în timp ce amortizarea fiscală (deducerea reală) se introduce separat, la P11. Omiterea add-back-ului contabil subevaluează impozitul declarat.

## Ce se greșește în practică

Cea mai frecventă cauză a unei astfel de omisiuni e corectarea ulterioară a unui mijloc fix (valoare de intrare, durată, dată PIF) fără reluarea manuală a amortizării fiscale/contabile în D101 deja generată.

## Ce face iConta.eu

Corectarea unui mijloc fix (valoare de intrare, durată normală de funcționare, dată punere în funcțiune) schimbă amortizarea fiscală recalculată de contabil, care intră direct în P11 (deducere) și, unde e cazul, în rollup-ul P28/P34 (add-back contabil) din D101. iConta.eu NU recalculează retroactiv o D101 deja generată la o corecție de mijloc fix — ajustarea trebuie reintrodusă manual în declarație. Motorul de amortizare pe mijloace fixe (`core/d406_active.py`, folosit și la controlul încrucișat cu registrul de active) calculează acum amortizarea pe fiecare metodă din activ — liniară, degresivă, accelerată și superaccelerată (CF art.28 alin.(6)-(8^1)): limitarea anterioară („doar liniar", indiferent de metoda din registru) a fost închisă pe 13.08.2026 (`DECIZII.md`, testul `test_datorie_mf_metode_amortizare` a fost eliminat ca xfail). D101 tratează însă în continuare amortizarea ca intrare manuală — indiferent de metoda folosită, contabilul introduce valorile în P11/P28, aplicația nu le preia automat în declarație. iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`opanaf_206_2025_d101.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
