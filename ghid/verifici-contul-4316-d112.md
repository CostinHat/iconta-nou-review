---
title: Cum verifici contul 4316 cu D112?
description: Contul 4316 (CASS) trebuie să corespundă, pe rulaj creditor, cu suma codurilor 432 și 459 din D112 — 459 fiind suprataxa angajatorului la contractele part-time, contabilizată tot aici, nu separat.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verifici contul 4316 cu D112?

Contul 4316 grupează contribuția de asigurări sociale de sănătate (CASS) datorată de angajați, iar în D112 ea apare sub două coduri, nu unul singur — la fel ca la CAS/4315. Ignorarea celui de-al doilea cod duce la o comparație greșită.

## Temeiul legal

::: ghid-temei
"Cota de contribuție de asigurări sociale de sănătate este de 10%..." — Codul fiscal (Legea 227/2015), art. 156
:::

Rulajul creditor al contului **4316** trebuie să corespundă cu **suma** codurilor **432** și **459** din D112:

- **432** — CASS calculat pe cota de 10%, conform art. 156 din Codul fiscal, aplicată bazei de contribuții a fiecărui angajat.
- **459** — suprataxa CASS datorată de angajator la anumite contracte part-time sub pragul minim. Se contabilizează tot în 4316, prin conturile de cheltuială aferente (6453), nu separat.

Toleranța de comparație e maximul dintre 1 leu și 0,5 lei înmulțit cu numărul de salariați ai lunii — nu o valoare fixă — pentru că D112 rotunjește totalul la leu, iar diferențele individuale de rotunjire se acumulează cu efectivul de personal.

Când diferența depășește toleranța, verifică în ordine: statul de plată a fost contabilizat? nota există dar e în ciornă (nevalidată)? au fost modificări ulterioare (salariați adăugați/șterși, corecții, concedii medicale)? Contul 4316 nu ar trebui ajustat manual doar ca să corespundă cu D112, fără identificarea cauzei.

## Ce se greșește în practică

Ca și la CAS, greșeala frecventă e compararea contului 4316 doar cu codul 432 din D112, ignorând codul 459 — la firmele cu angajați part-time sub pragul minim, asta produce o diferență aparentă care e de fapt suprataxa, corect contabilizată.

## Ce face iConta.eu

Maparea `COD_CONT_D112` din `core/control_incrucisat.py` însumează codurile 432 și 459 înainte de comparație cu rulajul contului 4316. Toleranța se recalculează pentru fiecare lună, în funcție de numărul de salariați activi în luna respectivă.

[iConta.eu](/)
