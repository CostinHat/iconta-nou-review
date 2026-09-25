---
title: "Cum se actualizează contractele de muncă la noul salariu minim"
description: "Obligația de a majora salariul contractual la nivelul noului salariu minim brut și termenul de raportare a modificării în REGES-ONLINE."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se actualizează contractele de muncă la noul salariu minim

Când salariul de bază minim brut pe țară crește prin hotărâre de guvern, orice contract de muncă în care salariul contractual a rămas sub noul nivel trebuie actualizat — legea nu permite plata unui salariu sub minimul legal, indiferent ce prevede contractul individual de muncă în vigoare.

## Temeiul legal

::: ghid-temei
„Începând cu data de 1 iulie 2026, salariul de bază minim brut pe țară garantat în plată, prevăzut la art. 164 alin. (1) din Legea nr. 53/2003 - Codul muncii, republicată, cu modificările și completările ulterioare, se stabilește în bani, fără a include sporuri și alte adaosuri, la suma de 4.325 lei lunar, pentru un program normal de lucru în medie de 166,667 ore pe lună, reprezentând 25,949 lei/oră."
— HG 146/2026 (sursă: anaf_surse/hg_146_2026_salariu_minim.txt)
:::

Pașii de actualizare, o dată ce noul plafon intră în vigoare:

- **Identifică toate contractele cu salariu de bază sub noul minim** — verificarea se face pe salariul de bază (fără sporuri și adaosuri), exact componenta la care se raportează hotărârea de guvern.
- **Încheie act adițional la contractul individual de muncă**, prin care salariul de bază se majorează la cel puțin noul nivel minim, cu data de la care se aplică (data intrării în vigoare a hotărârii de guvern, nu o dată ulterioară aleasă arbitrar).
- **Raportează modificarea în REGES-ONLINE** — o modificare a salariului (element de la art. 4 alin. (2) lit. j) din HG 295/2025) se transmite în registru în termen de 20 de zile lucrătoare de la data producerii modificării, termen mai lung decât pentru celelalte tipuri de modificări ale contractului.
- **Verifică efectul asupra altor sporuri/indemnizații** calculate ca procent din salariul minim (de exemplu unele facilități fiscale sau plafoane legate explicit de salariul minim) — majorarea salariului de bază poate schimba și alte calcule conexe.

## Ce se greșește în practică

- Se majorează salariul brut total (inclusiv sporuri) fără să se verifice dacă salariul de bază, separat, ajunge la noul minim — hotărârea de guvern se raportează explicit la salariul de bază, fără sporuri și adaosuri.
- Se aplică noul salariu minim în statul de plată, dar se omite încheierea actului adițional la contractul individual de muncă, care rămâne, formal, cu salariul vechi.
- Se transmite modificarea salariului în REGES-ONLINE cu întârziere peste termenul de 20 de zile lucrătoare, confundându-l cu termenul mai scurt (3 zile lucrătoare) aplicabil altor tipuri de modificări ale contractului.

## Ce face iConta.eu

iConta.eu calculează salariul și contribuțiile aferente (`core/salarizare.py`, funcția `calcul_salariu`) pe baza salariului brut introdus pentru fiecare salariat, iar pentru raportarea modificărilor contractuale către REGES-ONLINE există un client dedicat (`core/reges_client.py`, funcția `mesaj_adaugare_contract`), care generează mesajul XML de modificare a contractului. La data acestui ghid, aplicația **nu identifică automat, la fiecare actualizare a plafonului legal, contractele cu salariu de bază sub noul minim** — verificarea fiecărui contract și inițierea actului adițional rămân un pas manual, pe care contabilul îl parcurge folosind datele de salarizare deja introduse în aplicație.

[iConta.eu](/)
