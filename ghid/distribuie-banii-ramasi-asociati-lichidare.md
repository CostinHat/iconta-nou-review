---
title: Cum se distribuie banii rămași către asociați la lichidare?
description: Distribuirea sumelor rămase după plata datoriilor firmei ține de procedura de lichidare, nu de decontările curente cu asociații — dar folosește aceeași cotă de impozit ca dividendul.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se distribuie banii rămași către asociați la lichidare?

Această întrebare ține, strict, de procedura de **lichidare/radiere a societății**, nu de decontările curente cu asociații pe care le presupune o firmă activă (dividende, împrumuturi). Sunt două funcționalități diferite ale contabilității: cea de decontări asociați se ocupă de distribuirile din activitatea curentă a firmei, în timp ce partajul activului net rămas la lichidare e un proces distinct, care are loc o singură dată, la închiderea firmei.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend."
— Legea 31/1990, art. 67 alin. (1)
:::

La lichidare, sumele rămase după stingerea tuturor datoriilor firmei (inclusiv către bugetul de stat) se împart între asociați proporțional cu cota de participare la capitalul social — aceeași logică de proporționalitate din art. 67 alin. (1), aplicată însă activului net rămas, nu profitului curent. Partea din acest activ net care depășește capitalul social vărsat inițial de fiecare asociat e, în esență, tratată similar unui dividend și impozitată cu aceeași cotă (16% din 2026, conform Legii 141/2025). Procedura propriu-zisă de lichidare este reglementată separat, prin OMFP 897/2015 și Legea 31/1990 (dispozițiile despre dizolvare/lichidare), respectiv Legea 85/2014 dacă lichidarea are loc în cadrul unei proceduri de insolvență — texte care nu au fost citate verbatim în dosarul care stă la baza acestui ghid și trebuie verificate separat, la nevoie.

## Ce se greșește în practică

- Se distribuie „ce a rămas în cont" către asociați fără să se fi stins mai întâi toate datoriile firmei (inclusiv cele fiscale) — ordinea corectă e întotdeauna: se achită datoriile, apoi se distribuie ce rămâne.
- Se tratează toată suma distribuită ca fiind neimpozabilă, pe motiv că „e doar restituirea capitalului" — doar partea egală cu capitalul social vărsat inițial e neimpozabilă; ce depășește acest nivel se impozitează, de regulă, similar dividendului.
- Se calculează partajul înainte de a stinge soldurile de decontare deja existente cu asociații (împrumuturi nerestituite, dividende interimare neregularizate) — acestea trebuie lămurite înainte de partajul final.

## Ce face iConta.eu

Distribuirea la lichidare este acoperită de o funcționalitate separată de „Decontări asociați" — cea de **lichidare/radiere societate** — care calculează partajul folosind capitalul social, rezervele și profitul nedistribuit (`1012 = 456`, `106x/1171 = 456`), aplică impozitul pe partea asimilată dividendului cu aceeași cotă valabilă la data operațiunii (`456 = 446`) și înregistrează plata netă către asociați (`456 = 5121`). Funcționalitatea „Decontări asociați" descrisă în acest ghid rămâne relevantă doar înainte de lichidare, pentru soldurile de dividende și împrumuturi care trebuie stinse anterior partajului final.

[iConta.eu](/)
