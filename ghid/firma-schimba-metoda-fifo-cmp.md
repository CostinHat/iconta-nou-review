---
title: "Poate firma schimba metoda FIFO cu CMP?"
description: "Ce spune legea despre alegerea și schimbarea metodei de evaluare a stocurilor (FIFO, CMP, LIFO), și de ce iConta.eu nu oferă un comutator între ele."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Poate firma schimba metoda FIFO cu CMP?

Da, în principiu — metoda de evaluare a stocurilor este o alegere de politică contabilă a firmei, nu o obligație legală fixă pentru un anumit tip de activitate, așa că nimic nu interzice trecerea de la FIFO la CMP. Important e ca schimbarea să fie una reală și justificată, nu o simplă comoditate de moment, pentru că politicile contabile trebuie aplicate cu consecvență de la o perioadă la alta.

## Temeiul legal

::: ghid-temei
„96. - (1) Costul de achiziție sau costul de producție al stocurilor din aceeași categorie și al tuturor elementelor fungibile se calculează prin aplicarea uneia din următoarele metode: a) metoda costului mediu ponderat - CMP; ... b) metoda primul intrat-primul ieșit - FIFO; ... c) metoda ultimul intrat-primul ieșit - LIFO."
— OMFP 1802/2014, pct. 96 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- Legea nu leagă alegerea metodei de tipul de activitate sau de mărimea firmei — formularea „uneia din următoarele metode" lasă alegerea deschisă.
- Nu există, în textul pct. 96 alin. (1)-(4), nicio interdicție explicită de a schimba metoda aleasă inițial și nicio condiție specifică atașată acestei schimbări.
- În contabilitate, ca principiu general, o schimbare de politică contabilă (inclusiv a metodei de evaluare a stocurilor) trebuie să fie justificată și documentată, nu aplicată retroactiv fără motiv — dar textul exact al acestui principiu, aplicat punctual la schimbarea FIFO↔CMP, nu face parte din citatele verificate pentru acest ghid, așa că nu îl reproducem aici; pentru o schimbare efectivă, verificați prevederile complete despre permanența metodelor din OMFP 1802/2014 și, dacă e cazul, consultați un expert contabil.
- Practic, orice schimbare de metodă trebuie reflectată corect în evidența tehnico-operativă (fișele de magazie) de la data schimbării, nu recalculată retroactiv peste ieșirile deja înregistrate.

## Ce se greșește în practică

- Se schimbă metoda de evaluare fără nicio documentare internă a deciziei, ceea ce ridică întrebări la un control ulterior.
- Se recalculează retroactiv stocul existent după noua metodă, în loc să se aplice metoda nouă doar mișcărilor viitoare.
- Se presupune că schimbarea metodei e o simplă setare tehnică, fără impact contabil — de fapt, poate schimba valoarea stocului final și, implicit, rezultatul perioadei.

## Ce face iConta.eu

Această întrebare presupune o funcționalitate care **nu există în iConta.eu**: nu există, nicăieri în codul aplicației, un comutator sau o setare care să permită alegerea sau schimbarea metodei de evaluare între FIFO și CMP. Motorul de stocuri cantitativ-valorice (`core/stocuri_cv.py`) implementează exclusiv metoda CMP, fără nicio ramură alternativă pentru FIFO sau LIFO — costul se calculează mereu ca medie ponderată (`cmp_curent = valoare / cantitate`), indiferent de preferințele firmei.

Așadar, un utilizator care caută în iConta.eu o opțiune „schimbă metoda FIFO cu CMP" nu o va găsi, pentru simplul motiv că aplicația nu a oferit niciodată FIFO ca alternativă — singura metodă disponibilă pentru gestiunea cantitativ-valorică este CMP. Dacă firma folosea efectiv FIFO în altă parte (pe hârtie sau în alt sistem) și trece la iConta, trecerea înseamnă, de fapt, adoptarea metodei CMP ca metodă unică de evidență în aplicație, nu o alegere între cele două în interiorul ei.

[iConta.eu](/)
