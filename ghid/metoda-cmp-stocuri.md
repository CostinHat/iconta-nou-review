---
title: Ce este metoda CMP la stocuri?
description: Costul mediu ponderat (CMP) evaluează ieșirile din stoc la o medie recalculată a costurilor de intrare, nu la costul unui lot anume — una dintre metodele admise de OMFP 1802/2014, pct. 96, pentru elementele fungibile din aceeași categorie.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce este metoda CMP și cum se calculează costul unei ieșiri din stoc?

Când cumperi același tip de marfă la prețuri diferite, de la lot la lot, ai nevoie de o regulă care spune la ce cost iese fiecare bucată vândută sau consumată — pentru că bucățile fizice, odată puse pe raft, nu mai poartă eticheta lotului din care provin. Costul mediu ponderat (CMP) rezolvă asta printr-o medie: nu urmărește loturile individual, ci un cost mediu care se recalculează la fiecare intrare nouă.

## Temeiul legal

::: ghid-temei
**OMFP nr. 1802/2014, pct. 96 alin. (1)**: *„Costul de achiziție sau costul de producție al stocurilor din aceeași categorie și al tuturor elementelor fungibile se calculează prin aplicarea uneia din următoarele metode [...]"* — reglementările admit trei metode: **a) costul mediu ponderat (CMP)**; **b) primul intrat-primul ieșit (FIFO)**; **c) ultimul intrat-primul ieșit (LIFO)**.

**Alin. (2)**: *„Metoda «costului mediu ponderat» (CMP) presupune calcularea costului fiecărui element pe baza mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei și a costului elementelor similare produse sau cumpărate în timpul perioadei. Media poate fi calculată periodic sau după fiecare recepție. Perioada de calcul nu trebuie să depășească durata medie de stocare."*
:::

## Cum funcționează CMP

La fiecare **intrare** de marfă, costul mediu ponderat se recalculează: se adună valoarea stocului existent cu valoarea noii intrări, iar suma se împarte la cantitatea totală rezultată. Noul CMP rămâne valabil pentru toate ieșirile următoare, până la următoarea intrare.

La fiecare **ieșire**, cantitatea ieșită se evaluează la CMP-ul curent (cel calculat la ultima intrare) — nu la costul din vreun lot anume. Valoarea ieșirii = cantitate × CMP curent.

Fișa de magazie ține evidența cronologică: fiecare mișcare (intrare sau ieșire) e urmată de soldul de cantitate, valoare și CMP rezultat, ca la orice moment să se poată reconstitui exact cum s-a ajuns la costul folosit.

## Un exemplu

::: ghid-exemplu
Stoc inițial: **100 buc** la CMP **10 lei/buc** → valoare stoc = 1.000 lei.

**Intrare**: 50 buc la 13 lei/buc → valoare intrare = 650 lei. Noul CMP = (1.000 + 650) / (100 + 50) = 1.650 / 150 = **11 lei/buc**.

**Ieșire**: 80 buc → valoare ieșire = 80 × 11 = **880 lei**. Sold rămas: 70 buc, valoare 1.650 − 880 = 770 lei (CMP rămâne 11 lei/buc, pentru că n-a mai intrat marfă nouă).
:::

## Ce se greșește în practică

- **Se calculează CMP o singură dată, la începutul lunii**, și se aplică neschimbat toată luna, deși au intrat loturi noi la prețuri diferite — varianta „după fiecare intrare" (folosită mai sus) recalculează la fiecare intrare, nu o dată pe lună; reglementările admit și varianta lunară, dar cele două nu se amestecă în aceeași evidență.
- **Se lasă o ieșire să depășească stocul existent** — semn că fișa de magazie nu mai e sincronizată cu intrările reale; o ieșire nu poate fi mai mare decât ce e disponibil la momentul ei.
- **Se schimbă metoda de evaluare de la o lună la alta** (CMP într-o lună, FIFO în alta) fără o politică contabilă consecventă — metoda de evaluare a stocurilor e o opțiune care se aplică constant, nu ad-hoc.

## Ce face iConta.eu

Fișa de magazie recalculează CMP-ul după fiecare intrare (valoarea stocului plus valoarea intrării, împărțită la cantitatea totală), iar fiecare ieșire se evaluează la CMP-ul rezultat din istoricul mișcărilor de până atunci. O ieșire care ar depăși stocul disponibil e respinsă, nu acceptată cu un sold negativ. Nota contabilă la ieșire urmează natura stocului — 607=371 pentru mărfuri, 601=301 pentru materii prime.

[iConta.eu](/)
