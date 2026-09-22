---
title: Cum se contabilizează comenzile ramburs?
description: Legea cere document justificativ pentru fiecare operațiune; încasarea efectivă a rambursului ajunge de regulă printr-o decontare bancară agregată, fără CUI-ul fiecărui client, așa că matching-ul automat pe factură nu funcționează pentru aceste linii — alocarea rămâne manuală.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se contabilizează comenzile ramburs?

Comenzile cu plata ramburs au un flux specific: factura se emite la livrare, dar banii ajung în cont abia mai târziu, printr-o decontare de la curier, care de regulă cumulează mai multe comenzi într-o singură linie bancară. Această întârziere și agregare afectează direct modul în care motorul de matching poate (sau nu) să lege automat încasarea de facturi.

## Temeiul legal

::: ghid-temei
**Articolul 6 (1)** Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ.

511 Valori de încasat [...] 512 Conturi curente la bănci [...] 5121 Conturi la bănci în lei [...] Contul 512 "Conturi curente la bănci" [...] este un cont bifuncțional. În debitul contului 512 [...] se înregistrează: [...] – sumele încasate de la clienți (411, 413); [...]
:::

## Ce se întâmplă în practică la reconciliere

Factura comenzii se emite la livrare, ca orice altă factură, și rămâne deschisă în evidență până la încasare. Când curierul virează decontarea, linia din extrasul bancar conține de regulă suma netă (după reținerea comisionului curierului) și textul agregatorului, nu CUI-ul fiecărui client care a plătit ramburs. Fără CUI detectat în descriere, motorul de matching marchează automat linia cu status roșu — indiferent de câte comenzi acoperă real suma decontată.

Practic, legătura dintre fiecare comandă ramburs și decontarea agregată nu poate fi făcută automat de motorul de matching din F073. E nevoie fie de alocare manuală a sumei pe facturile individuale corespunzătoare comenzilor din acea decontare, fie de un raport de settlement separat, în afara ariei `core/reconciliere.py`, care să identifice comenzile acoperite de fiecare decontare a curierului.

## Ce se greșește în practică

- Se așteaptă ca statusul roșu al liniei de decontare curier să dispară automat după recontrolarea extrasului — el rămâne roșu până la alocare manuală, pentru că lipsa CUI e structurală, nu o eroare temporară.
- Se contabilizează suma netă (după comisionul reținut) direct pe valoarea brută a facturilor, fără să se separe comisionul curierului ca operațiune distinctă.
- Se presupune că fiecare decontare corespunde exact unei singure comenzi — de regulă acoperă mai multe comenzi simultan, agregate de curier pe o perioadă.
- Se ignoră faptul că suma din extras poate diferi de suma facturată din cauza comisionului de curier, retururilor sau anulărilor procesate de curier înainte de decontare.

## Ce face iConta.eu

Motorul de matching (`core/reconciliere.py`) cere un CUI identificat pentru fiecare linie de extras înainte de a căuta facturi deschise ale partenerului. Liniile de decontare curier, fără CUI individual în descriere, primesc automat status roșu, alocări goale, motiv "fără CUI în descriere". Pentru aceste linii, sistemul poate propune o sugestie de cont bazată pe istoricul deja contat de utilizator (`core.ai_incredere.sugestie`), dar fără nicio bază legală atribuită — e o funcționalitate de confort.

Alocarea sumei decontate pe facturile individuale ale comenzilor ramburs rămâne, în această situație, un pas manual la contare, folosind parametrul `alocari`.

[iConta.eu](/)
