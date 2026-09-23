---
title: "Cum identific tranzacțiile bancare neînregistrate în contabilitate?"
description: Ecranul de reconciliere bancară afișează fiecare linie de extras cu o stare vizibilă — necontată, parțial potrivită sau ignorată — ceea ce îți arată direct ce operațiuni au ajuns deja în contabilitate și ce a rămas afară.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum identific tranzacțiile bancare neînregistrate în contabilitate?

O tranzacție bancară „neînregistrată" înseamnă că a intrat în extrasul importat, dar nu a generat încă o notă contabilă. Modulul de reconciliere marchează fiecare linie de extras cu o stare, exact pentru a face vizibilă această diferență, fără să fie nevoie să compari manual extrasul cu jurnalul contabil.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ." — Legea contabilității nr. 82/1991, art. 6 alin. (1)
:::

Extrasul de cont este el însuși document justificativ pentru operațiunile bancare, alături de contractele și documentele financiar-contabile aferente (OMFP nr. 2634/2015, Anexa 1, pct. 25) — de aici obligația ca fiecare linie din el să ajungă, într-un fel sau altul, într-o înregistrare contabilă.

## Cum identifici liniile neînregistrate

După importul extrasului, fiecare linie primește automat o stare, în funcție de rezultatul potrivirii cu facturile deschise ale partenerului:

- **fără potrivire** — nu s-a găsit un CUI de partener recunoscut în descrierea liniei, sau CUI-ul există dar partenerul nu are nicio factură deschisă pe direcția respectivă (încasare → facturi emise, plată → facturi primite);
- **potrivire parțială** — suma nu corespunde exact cu o factură sau o combinație de facturi, și s-a propus o alocare pe cea mai veche factură deschisă (FIFO), eventual parțial;
- **potrivire exactă** — suma corespunde exact cu o factură sau o combinație de facturi ale aceluiași partener.

Doar liniile pe care le confirmi explicit (butonul de contare) generează notă contabilă — până atunci, ele rămân vizibile ca neînregistrate pe ecranul Bancă, indiferent de starea potrivirii.

## Ce se greșește în practică

- Se citește doar rezultatul potrivirii automate (starea liniei) și se presupune că orice linie „potrivită" a fost deja și contabilizată — potrivirea și contabilizarea sunt doi pași distincți.
- Se ignoră liniile fără potrivire în loc să fie investigate — de multe ori lipsa potrivirii vine dintr-un CUI absent din descrierea bancară, nu dintr-o operațiune inexistentă.
- Se lasă linii neprocesate mai multe luni, ceea ce face mai greu de reconstituit contextul operațiunii (de exemplu, factura la care se referea plata) la momentul corectării.

## Ce face iConta.eu

La importul unui extras, iConta.eu afișează fiecare linie cu un indicator vizual al stării de potrivire (fără potrivire, potrivire parțială, potrivire exactă), plus starea de contabilizare (contată sau nu). Din același ecran poți contabiliza o linie potrivită automat, poți alege manual facturile pe care se alocă o sumă, sau poți ignora explicit o linie care nu trebuie contabilizată — fără să treci de la extras la jurnalul contabil pentru a face comparația.

[iConta.eu](/)
