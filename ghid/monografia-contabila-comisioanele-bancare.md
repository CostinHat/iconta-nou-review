---
title: "Care este monografia contabilă pentru comisioanele bancare?"
description: "Contul din reglementările contabile românești folosit pentru evidențierea comisioanelor bancare și logica lui de funcționare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este monografia contabilă pentru comisioanele bancare?

Comisioanele reținute de bancă pentru operațiuni curente (administrare cont, transfer, mentenanță card, procesare plăți) se înregistrează într-un cont dedicat din planul general de conturi, distinct de dobânzi sau de alte cheltuieli financiare. Reglementările contabile aprobate prin OMFP 1802/2014 descriu explicit conținutul și funcționarea acestui cont.

## Temeiul legal

::: ghid-temei
„Contul 627 «Cheltuieli cu serviciile bancare și asimilate». Cu ajutorul acestui cont se ține evidența cheltuielilor cu serviciile bancare și asimilate. În debitul contului 627 «Cheltuieli cu serviciile bancare și asimilate» se înregistrează: – valoarea serviciilor bancare și asimilate plătite (471, 512); – sume clarificate trecute pe cheltuieli (473)."
— OMFP nr. 1.802/2014 pentru aprobarea reglementărilor contabile (sursă: anaf_surse/omfp_1802_2014.txt)
:::

Practic, monografia standard pentru un comision bancar plătit direct din contul curent este:

- **627 „Cheltuieli cu serviciile bancare și asimilate" = 5121 „Conturi la bănci în lei"** — pentru comisionul debitat direct din extrasul de cont, fără factură separată emisă anterior.
- Dacă suma a fost înregistrată inițial ca sumă în clarificare (situații neclare la data extrasului): **627 = 473 „Decontări din operațiuni în curs de clarificare"**, urmată de clarificarea ulterioară a operațiunii.

Contul 627 face parte din grupa 62 „Cheltuieli cu alte servicii executate de terți" din planul de conturi general, alături de conturi precum 628 „Alte cheltuieli cu serviciile executate de terți", folosit pentru alte tipuri de servicii prestate de terți care nu se încadrează la comisioane bancare propriu-zise.

## Ce se greșește în practică

- Se înregistrează comisioanele bancare direct în contul 628 „Alte cheltuieli cu serviciile executate de terți", deși legea prevede un cont specific (627) pentru această categorie.
- Se omite deducerea TVA aferentă comisioanelor bancare fără să se verifice mai întâi dacă operațiunea e într-adevăr scutită de TVA — majoritatea serviciilor bancare sunt scutite fără drept de deducere, deci de regulă nu există TVA de recuperat, dar unele servicii accesorii (de exemplu anumite comisioane de consultanță financiară) pot fi taxabile.
- Se contabilizează comisionul brut fără să se separe eventualele componente diferite (de exemplu comision + TVA, dacă banca aplică TVA pe un serviciu specific), ceea ce denaturează atât cheltuiala, cât și eventuala taxă deductibilă.
- Se confundă dobânda bancară (cont 666 „Cheltuieli privind dobânzile") cu comisionul bancar (cont 627) — sunt cheltuieli de natură diferită, cu tratament fiscal distinct la calculul impozitului pe profit (dobânzile pot intra sub incidența unor limitări specifice privind costurile îndatorării).

## Ce face iConta.eu

iConta.eu **recunoaște și contează automat operațiunile bancare** importate din extrasul de cont, inclusiv comisioanele bancare, prin modulele dedicate de import și parsare a extraselor (`banca.py`, `banca_parser.py`). Aplicația poate identifica liniile de extras corespunzătoare comisioanelor și le poate propune spre contare pe conturile corespunzătoare, reducând munca manuală de clasificare, dar decizia finală privind încadrarea exactă (627 vs. alt cont, în funcție de politica contabilă a firmei) rămâne la latitudinea utilizatorului sau a contabilului care validează notele contabile.

[iConta.eu](/)
