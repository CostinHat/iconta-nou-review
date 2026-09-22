---
title: Cum se reconciliază rambursurile de la curier cu facturile?
description: Legea cere ca orice operațiune să aibă un document justificativ; motorul de matching nu identifică automat CUI-ul clienților individuali dintr-o linie de decontare agregată de la curier, așa că aceste linii cad sistematic pe status roșu și necesită alocare manuală.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se reconciliază rambursurile de la curier cu facturile?

Firmele care vând cu plata ramburs primesc de la curier, de regulă, o singură linie de decontare bancară agregată, care acoperă zeci sau sute de comenzi individuale. Întrebarea e dacă motorul de matching poate lega automat această linie de facturile corespunzătoare — răspunsul onest e că nu poate, și e important de știut de ce.

## Temeiul legal

::: ghid-temei
**Articolul 6 (1)** Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. **(2)** Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz.
:::

## De ce linia de decontare curier cade pe roșu

Motorul de matching identifică facturile unui partener pe baza CUI-ului extras din descrierea liniei bancare. O decontare de ramburs de la curier conține, de regulă, un singur transfer agregat, cu textul curierului în descriere (de exemplu "DECONTARE RAMBURS"), nu CUI-ul fiecărui client final care a plătit ramburs la livrare. Fără CUI detectat, motorul marchează automat linia cu status roșu, motivul fiind explicit "fără CUI în descriere" — indiferent de câte facturi individuale acoperă real suma decontată.

Nu există în motorul de matching (`core/reconciliere.py`) niciun mecanism de "matching pe lot", care să lege o singură linie de decontare agregată de N facturi individuale. Pentru a înregistra corect aceste încasări, e nevoie fie de alocare manuală linie cu linie, fie de un raport separat de settlement (în afara ariei acestui motor), care să identifice comenzile individuale acoperite de decontare.

## Ce se greșește în practică

- Se așteaptă ca sistemul să potrivească automat decontarea de ramburs cu toate comenzile aferente — motorul nu are acces la lista de comenzi din spatele decontării agregate, doar la suma și descrierea liniei bancare.
- Se lasă liniile roșii de decontare curier necontate, considerându-se eronat "eroare de sistem", deși e comportamentul așteptat pentru o linie fără CUI.
- Se contabilizează suma agregată direct pe o singură factură arbitrară, doar ca să "dispară" din lista de linii neprocesate, fără legătură reală cu operațiunile individuale.
- Se ignoră diferența dintre comisionul reținut de curier și suma efectiv facturată către client — decontarea netă primită nu corespunde întotdeauna sumei brute din facturi.

## Ce face iConta.eu

`core/reconciliere.py` cere un CUI identificat pentru fiecare linie de extras (populat în amonte, prin extragerea automată din descriere) înainte de a căuta facturi deschise ale partenerului. O linie fără CUI detectat primește direct status roșu, alocări goale. Pentru liniile roșii fără notă manuală, sistemul încearcă o sugestie de cont pe baza istoricului deja contat (`core.ai_incredere.sugestie`) — o funcționalitate de confort, fără bază legală, utilizatorul rămânând responsabil de validare.

Pentru decontările agregate de ramburs, alocarea pe facturile individuale rămâne un pas manual, folosind parametrul `alocari` la contare (`conteaza`) pentru a specifica exact ce facturi se sting.

[iConta.eu](/)
