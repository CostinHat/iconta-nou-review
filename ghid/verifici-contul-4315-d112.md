---
title: Cum verifici contul 4315 cu D112?
description: Contul 4315 (CAS) trebuie să corespundă, pe rulaj creditor, cu suma codurilor 412 și 458 din D112 — 458 fiind suprataxa angajatorului la contractele part-time, contabilizată tot aici, nu separat.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici contul 4315 cu D112?

Contul 4315 grupează contribuția de asigurări sociale (CAS) datorată de angajați, iar în D112 ea apare sub două coduri distincte, nu unul singur. Confuzia frecventă e ignorarea celui de-al doilea cod, ceea ce duce la o comparație greșită.

## Temeiul legal

::: ghid-temei
"25% datorată de către persoanele fizice care au calitatea de angajați..." — Codul fiscal (Legea 227/2015), art. 138 lit. a)
:::

Rulajul creditor al contului **4315** trebuie să corespundă cu **suma** codurilor **412** și **458** din D112, nu doar cu 412:

- **412** — CAS calculat pe cota de 25%, conform art. 138 lit. a) din Codul fiscal, aplicată bazei de contribuții a fiecărui angajat.
- **458** — suprataxa CAS datorată de angajator la anumite contracte part-time (sub pragul stabilit prin regula "podelei" salariului minim). Deși e o obligație distinctă a angajatorului, se contabilizează tot în 4315, prin conturile de cheltuială aferente (6451), nu într-un cont separat.

Toleranța de comparație nu e fixă: e maximul dintre 1 leu și 0,5 lei înmulțit cu numărul de salariați ai lunii — pentru că D112 rotunjește totalul la leu, iar rotunjirile individuale pe fiecare salariat se acumulează.

Când diferența depășește toleranța, cauza cea mai probabilă e una din: statul de plată nu a fost contabilizat, nota există dar e în ciornă, sau au apărut modificări ulterioare (salariați adăugați/șterși, corecții de lună anterioară, concedii medicale calculate diferit).

## Ce se greșește în practică

Greșeala frecventă e compararea contului 4315 doar cu codul 412, ignorând 458 — la firmele cu angajați part-time sub pragul minim, asta produce o diferență falsă, pentru că suprataxa e reală și contabilizată corect, dar necuprinsă în comparația manuală.

## Ce face iConta.eu

Maparea din `core/control_incrucisat.py` (`COD_CONT_D112`) însumează automat codurile 412 și 458 înainte de a compara cu rulajul contului 4315, exact pentru a evita această greșeală. Toleranța se calculează dinamic în funcție de numărul de salariați ai lunii verificate.

[iConta.eu](/)
