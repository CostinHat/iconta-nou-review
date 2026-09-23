---
title: Cum aleg metoda de evaluare a stocurilor la ieșire?
description: Legea permite CMP, FIFO sau LIFO pentru stocuri fungibile obișnuite, plus metoda prețului cu amănuntul pentru comerțul cu amănuntul cu articole numeroase și marje similare; iConta implementează doar CMP (cantitativ-valoric) și metoda global-valorică — FIFO și LIFO nu sunt disponibile ca funcționalitate.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum aleg metoda de evaluare a stocurilor la ieșire?

Legea contabilă lasă firma să aleagă între mai multe metode de evaluare a stocurilor la ieșirea din gestiune, dar alegerea nu e liberă la infinit — depinde de tipul de activitate, iar odată aleasă, metoda trebuie aplicată consecvent. Mai jos, opțiunile legale și ce anume acoperă, concret, aplicația.

## Temeiul legal

::: ghid-temei
„96. - (1) Costul de achiziție sau costul de producție al stocurilor din aceeași categorie și al tuturor elementelor fungibile se calculează prin aplicarea uneia din următoarele metode: a) metoda costului mediu ponderat - CMP; b) metoda primul intrat-primul ieșit - FIFO; c) metoda ultimul intrat-primul ieșit - LIFO. (2) Metoda «costului mediu ponderat» (CMP) presupune calcularea costului fiecărui element pe baza mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei și a costului elementelor similare produse sau cumpărate în timpul perioadei. ... (3) Potrivit metodei «primul intrat-primul ieșit» (FIFO), bunurile ieșite din gestiune se evaluează la costul de achiziție sau de producție al primei intrări (lot). ... (4) Potrivit metodei «ultimul intrat-primul ieșit» (LIFO), bunurile ieșite din gestiune se evaluează la costul de achiziție sau de producție al ultimei intrări (lot). ...”

„(8) În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă. ...”

— *OMFP 1802/2014, pct. 96 și pct. 286 alin. (8).*

„Metoda trebuie aplicată consecvent pentru elemente similare de natura stocurilor ... de la un exercițiu financiar la altul. Dacă, într-un caz excepțional, ... se schimbă metoda pentru un anumit element de stocuri, ... se prezintă în notele explicative: motivul schimbării metodei ... și efectele sale asupra rezultatului.”

— *OMFP 1802/2014, pct. 287 alin. (1)-(2) (rezumat consecvența metodei).*
:::

## Cele patru opțiuni legale, pe scurt

1. **CMP (cost mediu ponderat)** — costul se recalculează ca medie ponderată, după fiecare recepție sau periodic. Potrivită pentru stocuri fungibile, cu mișcare pe articol individual (materii prime, marfă evidențiată cantitativ pe fiecare produs).
2. **FIFO** — marfa iese din gestiune la costul primului lot intrat, în ordine cronologică.
3. **LIFO** — marfa iese la costul ultimului lot intrat.
4. **Metoda prețului cu amănuntul (global-valorică)** — rezervată explicit comerțului cu amănuntul, cu articole numeroase și marje similare, unde nu e practic să se urmărească fiecare articol separat; costul vândut se determină prin deducerea marjei brute din prețul de vânzare, nu prin urmărirea costului fiecărui lot.

Alegerea depinde de natura activității: un magazin cu multe articole mărunte (băcănie, farmacie, papetărie) se pretează la metoda global-valorică; o activitate cu articole puține, de valoare mare sau urmărite individual (materii prime pentru producție, marfă cu preț de achiziție variabil) se pretează la CMP/FIFO/LIFO.

## Ce se greșește în practică

- Se schimbă metoda de la un an la altul fără motiv documentat și fără prezentarea efectelor în notele explicative — legea cere consecvență, cu excepție justificată explicit.
- Se presupune că metoda global-valorică e obligatorie pentru orice magazin cu amănuntul — legea o permite, nu o impune; un magazin poate ține și evidență cantitativ-valorică pe articol, dacă preferă.
- Se caută FIFO sau LIFO ca opțiune de configurare într-o aplicație care nu le implementează, presupunând că sunt disponibile pentru că sunt permise de lege.

## Ce face iConta.eu

iConta implementează **două** din cele patru metode legale, nu toate:

- **Metoda cantitativ-valorică (CMP)** — `core/stocuri_cv.py` + `core/stocuri_cv_api.py`, cu cost mediu ponderat recalculat după fiecare intrare, fișă de magazie cronologică per articol și validare cronologică (o ieșire nu poate depăși stocul la data ei).
- **Metoda global-valorică (preț cu amănuntul)** — `core/stocuri.py` + `core/stocuri_api.py`, cu coeficient de repartizare K, descrisă pe larg în ghidurile dedicate contului 378 și adaosului comercial.

**FIFO și LIFO nu sunt implementate** ca metodă de evaluare la ieșire — nu există, în codul verificat, niciun modul care să urmărească loturi de intrare în ordine cronologică pentru scoaterea din gestiune la costul primului sau ultimului lot. Dacă activitatea firmei impune, legal sau operațional, FIFO ori LIFO, calculul respectiv nu poate fi automatizat momentan prin iConta — rămâne de făcut manual, în afara aplicației.

[iConta.eu](/)
