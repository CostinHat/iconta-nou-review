---
title: "Chitanța fiscală vs chitanța simplă: când folosesc fiecare"
description: "Diferența dintre bonul fiscal emis de aparatul de marcat electronic (numit popular «chitanță fiscală») și chitanța document justificativ din OMFP 2634/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Chitanța fiscală vs chitanța simplă: când folosesc fiecare

„Chitanță fiscală" e un termen popular, nu unul folosit de actele normative — ceea ce numim așa e de fapt **bonul fiscal**, emis obligatoriu de aparatul de marcat electronic fiscal (AMEF). Chitanța, ca document distinct, e reglementată separat, de o altă normă, pentru alte situații.

## Temeiul legal

::: ghid-temei
„(8) [...] operatorii economici utilizatori sunt obligați să înregistreze într-un registru special, întocmit în acest sens, toate operațiunile efectuate și să emită chitanțe, în condițiile legii, pentru respectivele operațiuni și facturi, la cererea clientului."
— OUG 28/1999, art. 1 alin. (8) (sursă: anaf_surse/oug_28_1999.html)

„Chitanța și chitanța pentru operațiuni în valută sunt documente justificative de înregistrare în registrul de casă/registrul de casă în valută și în contabilitate a încasărilor și plăților efectuate în numerar (lei/valută) [...]. În condițiile utilizării aparatelor de marcat electronice fiscale, în conformitate cu prevederile legale, documentul în baza căruia se înregistrează în contabilitate veniturile aferente încasărilor zilnice este Raportul fiscal de închidere zilnică."
— OMFP 2634/2015, Anexa 2, Cod 14-4-1 (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Distincția, aplicată:

- **Bonul fiscal** (numit popular "chitanță fiscală") se emite **obligatoriu de AMEF**, la fiecare vânzare cu amănuntul sau prestare de serviciu către populație plătită în numerar (OUG 28/1999). El e documentul fiscal al vânzării, colectat automat de aparat.
- **Chitanța** (Cod 14-4-1) e documentul justificativ pentru încasări **fără AMEF** — între firme, pentru operațiuni scutite fără drept de deducere, sau, expres, în perioada de **defectare a casei de marcat**, când legea obligă explicit la emiterea de chitanțe în locul bonului fiscal.
- Nu se folosesc alternativ, la alegere: firma care are obligația AMEF (vânzare cu amănuntul, servicii către populație) emite bon fiscal ca regulă; recurge la chitanță doar când legea o cere sau permite explicit (fără AMEF, defectare).

## Ce se greșește în practică

- Se numește orice document de încasare "chitanță fiscală", fără să se distingă dacă e vorba de bonul emis de aparatul de marcat sau de formularul de chitanță (Cod 14-4-1) — confuzia terminologică duce, uneori, și la confuzie de regim fiscal aplicabil.
- Se emite chitanță în locul bonului fiscal pentru vânzări cu amănuntul curente, deși aparatul funcționează normal — legea rezervă chitanța pentru cazurile expres prevăzute, nu ca alternativă la liberă alegere.
- Se uită să se emită chitanță în perioada de defectare a AMEF, considerând că "fără bon fiscal nu se poate vinde" — OUG 28/1999 prevede exact opusul: se continuă activitatea, cu chitanțe și înregistrare în registrul special.

## Ce face iConta.eu

La data acestui ghid, `core/chitante.py` (`pdf_chitanta()`) generează chitanța document justificativ (Cod 14-4-1), pentru situațiile în care ea e cerută. Emiterea propriu-zisă a bonului fiscal rămâne, evident, în sarcina aparatului de marcat electronic fiscal — iConta.eu preia rezultatul lui prin `core/amef_import.py` (`parseaza_raport_z()`), care citește raportul de închidere zilnică, nu bonurile individuale.

[iConta.eu](/)
