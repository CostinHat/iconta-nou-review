---
title: 'Evidența global-valorică vs cantitativ-valorică 2026'
description: Global-valorică (preț cu amănuntul, conturile 371/378/4428) se potrivește magazinelor cu multe articole mărunte; cantitativ-valorică (CMP, pe fiecare articol) se potrivește activităților cu articole urmărite individual — cele două nu se pot combina pe aceeași gestiune.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Evidența global-valorică vs cantitativ-valorică 2026

Cele două metode răspund unor nevoi diferite: global-valorică urmărește valoarea totală a mărfii dintr-o gestiune, fără să țină evidența fiecărui articol separat; cantitativ-valorică urmărește fiecare articol, cu cantitate și cost propriu. Alegerea corectă depinde de tipul de activitate, nu de preferință.

## Temeiul legal

::: ghid-temei
„96. - (1) Costul de achiziție sau costul de producție al stocurilor din aceeași categorie și al tuturor elementelor fungibile se calculează prin aplicarea uneia din următoarele metode: a) metoda costului mediu ponderat - CMP; ...”

„286. - (1) ... pentru determinarea costului pot fi folosite, de asemenea, metoda costului standard, în activitatea de producție sau metoda prețului cu amănuntul, în comerțul cu amănuntul. (8) În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă.”

— *OMFP 1802/2014, pct. 96 și pct. 286.*

„Metoda trebuie aplicată consecvent ... se poate justifica folosirea de metode diferite pentru stocuri cu natură sau utilizare diferită.”

— *OMFP 1802/2014, pct. 287.*
:::

## Comparație directă

| | **Global-valorică (preț cu amănuntul)** | **Cantitativ-valorică (CMP)** |
|---|---|---|
| Ce urmărește | Valoarea totală a mărfii din gestiune, cu adaos separat pe 378 | Fiecare articol, cu cantitate și cost mediu ponderat propriu |
| Conturi cheie | 371 (mărfuri), 378 (adaos), 4428 (TVA neexigibilă) | 371/301 (marfă/materie primă), 607/601 (cost vândut) |
| Potrivită pentru | Articole numeroase, cu mișcare rapidă, marje similare — magazin alimentar, papetărie, farmacie | Articole puține sau de valoare mare, urmărite individual — materii prime pentru producție, marfă cu costuri diferite pe articol |
| Descărcare | Lunară, prin coeficient de repartizare (K) aplicat vânzărilor lunii | La fiecare vânzare/consum, prin costul mediu recalculat după fiecare intrare |
| Restricție | Nu se poate combina cu inventarul intermitent (pct. 291 alin. 5) | Cere validare cronologică — o ieșire nu poate depăși stocul la data ei |

Legea permite (pct. 287) folosirea de metode diferite pentru categorii de stocuri diferite în cadrul aceleiași firme — de exemplu, marfă de raft ținută global-valoric, dar materii prime pentru un mic atelier propriu ținute cantitativ-valoric — dar aceeași categorie de stocuri trebuie ținută consecvent, cu aceeași metodă, de la un exercițiu la altul.

## Ce se greșește în practică

- Se amestecă cele două metode pe aceeași gestiune (același cont 371, aceleași articole) — global-valorică și cantitativ-valorică sunt mecanisme de calcul incompatibile pe același set de date.
- Se schimbă metoda de la un an la altul fără motiv documentat în notele explicative.
- Se presupune că metoda global-valorică e „mai simplă”, deci implicit corectă pentru orice magazin mic — alegerea corectă depinde de natura articolelor (numeroase și cu marje similare vs. urmărite individual), nu de mărimea firmei.

## Ce face iConta.eu

iConta implementează cele două metode ca module separate, complet independente: **F088**, gestiunea global-valorică (`core/stocuri.py` + `core/stocuri_api.py`, coeficient K, conturile 371/378/4428) și **F089**, gestiunea cantitativ-valorică (`core/stocuri_cv.py` + `core/stocuri_cv_api.py`, cost mediu ponderat recalculat după fiecare intrare, fișă de magazie cronologică per articol). Nu există niciun cod care să lege cele două module — o firmă alege, la nivel de gestiune, care mecanism folosește, iar aplicația nu permite combinarea automată a lor pe aceleași articole.

[iConta.eu](/)
