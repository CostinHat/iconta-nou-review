---
title: "Cum contabilizez o factură achitată de salariat din bani proprii?"
description: "Regimul plăților în numerar din avansuri spre decontare, atunci când un angajat achită o factură a firmei din banii proprii și urmează să fie decontat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum contabilizez o factură achitată de salariat din bani proprii?

Situația e frecventă: un angajat plătește pe loc, din banii proprii, o factură mică a firmei (piese auto, birotică, o cursă de taxi), urmând să fie rambursat ulterior. Contabil, operațiunea trece prin decontarea unui avans de trezorerie — iar plata din avans, dacă se face în numerar, are propriul plafon legal.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...] e) plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare."
— Legea 70/2015 pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar, art. 3 alin. (1) lit. e), astfel cum a fost modificat prin OUG 115/2023 (sursă: anaf_surse/legea_70_2015_consolidat.html)
:::

Ce înseamnă practic pentru contabilizare:

- Suma plătită de angajat din banii proprii, pentru o cheltuială a firmei, se tratează ca decontare a unui avans de trezorerie — indiferent dacă avansul a fost acordat efectiv înainte (angajatul a primit bani și a plătit) sau se recunoaște retroactiv (angajatul a plătit din proprii bani, apoi firma îl rambursează).
- Plafonul zilnic de 5.000 lei se aplică per persoană care are avansuri spre decontare — dacă suma cheltuită de angajat într-o zi depășește acest plafon, rambursarea în numerar nu se poate face integral, ci doar până la plafon, restul prin instrumente de plată fără numerar.
- Documentul justificativ al cheltuielii (bonul fiscal, factura) rămâne obligatoriu pentru recunoașterea cheltuielii firmei, indiferent de sursa banilor folosiți pentru achitarea ei pe loc.

## Ce se greșește în practică

- Se rambursează angajatul integral în numerar, fără verificarea plafonului zilnic de 5.000 lei per persoană.
- Se înregistrează cheltuiala direct pe casă, fără să treacă prin contul de decontări cu personalul (avansuri de trezorerie), ceea ce denaturează evidența datoriilor firmei față de angajat.
- Se omite documentul justificativ al cheltuielii (bon/factură pe numele firmei), rambursând angajatul doar pe baza declarației sale.

## Ce face iConta.eu

Modulul de casierie al iConta.eu (`core/casa.py`) gestionează avansurile de trezorerie și verifică automat plafonul zilnic de 5.000 lei pentru plățile efectuate din avansuri spre decontare, pe fiecare persoană, semnalând ca avertisment orice depășire constatată, cu temeiul legal atașat.

[iConta.eu](/)
