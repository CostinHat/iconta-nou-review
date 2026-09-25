---
title: "Metoda LIFO mai este permisă în 2026"
description: "Este LIFO (ultimul intrat-primul ieșit) încă o metodă validă de evaluare a stocurilor la ieșirea din gestiune, conform reglementărilor contabile în vigoare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Metoda LIFO mai este permisă în 2026

Da — reglementările contabile românești nu au eliminat metoda LIFO (ultimul intrat-primul ieșit) dintre metodele acceptate de evaluare a stocurilor la ieșirea din gestiune. Ea rămâne, alături de CMP și FIFO, o opțiune legală.

## Temeiul legal

::: ghid-temei
„Costul de achiziție sau costul de producție al stocurilor din aceeași categorie și al tuturor elementelor fungibile se calculează prin aplicarea uneia din următoarele metode: a) metoda costului mediu ponderat - CMP; [...] b) metoda primul intrat-primul ieșit - FIFO; [...] c) metoda ultimul intrat-primul ieșit - LIFO. [...] Potrivit metodei «ultimul intrat-primul ieșit» (LIFO), bunurile ieșite din gestiune se evaluează la costul de achiziție sau de producție al ultimei intrări (lot). Pe măsura epuizării lotului, bunurile ieșite din gestiune se evaluează la costul de achiziție sau costul de producție al lotului anterior, în ordine cronologică."
— OMFP 1802/2014, pct. 96 alin. (1) și (4) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce trebuie reținut despre alegerea metodei:

- Metoda de evaluare la ieșire (CMP, FIFO sau LIFO) se alege de entitate și se aplică **consecvent** pentru toate stocurile de aceeași natură, de la o perioadă la alta.
- Nu am identificat, în textul consolidat al Codului fiscal, nicio prevedere care să interzică sau să restricționeze LIFO în scop fiscal — regula fiscală urmează, în acest punct, reglementarea contabilă.
- Schimbarea metodei de evaluare pe parcursul anului nu e o simplă opțiune administrativă — trebuie tratată ca o schimbare de politică contabilă, cu justificare și prezentare corespunzătoare în notele explicative.

## Ce se greșește în practică

- Se crede că LIFO a fost eliminat odată cu adoptarea IFRS la nivel internațional (unde LIFO e interzis) — regula IFRS nu se aplică automat entităților care raportează după reglementările naționale (OMFP 1802/2014).
- Se schimbă metoda de evaluare de la un an la altul fără nicio justificare documentată, doar pentru optimizarea rezultatului contabil — o schimbare de politică contabilă trebuie motivată și prezentată transparent.
- Se aplică metode diferite pentru gestiuni similare ale aceleiași entități, ceea ce face rezultatele necomparabile de la o gestiune la alta.

## Ce face iConta.eu

La acest moment, iConta.eu susține două dintre metodele acceptate: `core/stocuri.py` implementează metoda global-valorică (preț cu amănuntul), iar `core/stocuri_cv.py` implementează metoda cantitativ-valorică la cost mediu ponderat (CMP), recalculat după fiecare intrare (OMFP 1802/2014 pct. 96 alin. (2)). Aplicația nu oferă, la acest moment, evaluare pe loturi cronologice de tip FIFO sau LIFO; o firmă care aplică specific FIFO sau LIFO pe loturi va trebui să verifice dacă modulul de stocuri actual acoperă acest tip de evaluare pentru situația ei concretă.

[iConta.eu](/)
