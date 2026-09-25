---
title: "Cum aleg vectorul fiscal corect la înființare"
description: "Ce este vectorul fiscal al unei firme, ce alegeri conține și cum se stabilesc regimul de impozitare și obligația de TVA la înființare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum aleg vectorul fiscal corect la înființare

Vectorul fiscal e setul de atribute care spun ANAF-ului (și, practic, oricărui software de contabilitate) ce declarații datorează firma: regimul de impozit (micro sau profit), dacă e plătitoare de TVA, cu ce periodicitate depune decontul și dacă face operațiuni intracomunitare. Se stabilește prin declarația de înregistrare fiscală depusă la înființare și rămâne baza pentru toate obligațiile ulterioare.

## Temeiul legal

::: ghid-temei
„Persoana impozabilă care are sediul activității economice în România și realizează sau intenționează să realizeze o activitate economică ce implică operațiuni taxabile, scutite de taxa pe valoarea adăugată cu drept de deducere, cu locul în România, trebuie să solicite înregistrarea în scopuri de TVA la organul fiscal competent, după cum urmează: a) înainte de realizarea unor astfel de operațiuni, în următoarele cazuri: 1. dacă declară că urmează să realizeze o cifră de afaceri care depășește plafonul de scutire prevăzut la art. 310 alin. (1) [...]"
— Legea 227/2015 (Codul fiscal), art. 316 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce trebuie decis efectiv la înființare:

- **Regimul de impozitare**: micro (1% pe venituri, dacă sunt îndeplinite condițiile din art. 47 Cod fiscal) sau profit (16% pe profit) — nu e o alegere liberă, ci depinde de condițiile legale îndeplinite la data înregistrării.
- **Înregistrarea în scopuri de TVA**: obligatorie la depășirea plafonului legal, dar poate fi și opțională de la înființare, dacă firma anticipează operațiuni care o justifică.
- **Periodicitatea decontului de TVA** (lunar/trimestrial) și **operațiunile intracomunitare** — acestea determină dacă firma va depune D300 lunar sau trimestrial și dacă va depune D390.

## Ce se greșește în practică

- Se bifează „plătitor de TVA" din prudență, fără să se evalueze dacă firma se încadrează la neplătitor — asta generează obligații de declarare inutile pentru o firmă mică la început de drum.
- Se alege regimul micro fără verificarea condiției de a avea cel puțin un salariat în termenul legal (90 de zile de la înregistrare pentru firmele nou-înființate) — nerespectarea ei împinge firma automat pe impozit pe profit.
- Se completează vectorul fiscal o singură dată, la înființare, și nu se actualizează când firma trece pragurile (de exemplu plafonul de TVA sau plafonul de venituri pentru micro).

## Ce face iConta.eu

iConta.eu are un ecran dedicat „Date firmă" (`core/vector_fiscal_api.py`) unde se completează exact aceste patru atribute: regim fiscal, statutul de plătitor de TVA, periodicitatea decontului și operațiunile intracomunitare. Aplicația nu permite salvarea unui vector incomplet — cere explicit fiecare alegere, fără valori implicite tăcute, tocmai pentru că o valoare presupusă greșit duce la declarații lipsă mai târziu. Din acest vector, motorul de conformare al aplicației (`core/control_fiscal_api.py`) derivă automat ce declarații (D100, D300, D390, D101 etc.) sunt datorate lunar sau trimestrial. iConta.eu nu depune însă declarația de înregistrare fiscală la ANAF — aceasta rămâne un pas separat, făcut de contabil sau prin portalul ANAF.

[iConta.eu](/)
