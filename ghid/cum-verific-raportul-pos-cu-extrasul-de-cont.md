---
title: Cum verific raportul POS cu extrasul de cont?
description: Legea cere confruntarea soldurilor din extrasul de cont cu contabilitatea; decontările POS ajung agregat, fără CUI individual pe tranzacție, deci motorul de matching le marchează roșu, iar verificarea contra raportului POS rămâne un pas manual.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum verific raportul POS cu extrasul de cont?

Încasările cu cardul la POS nu apar în extrasul bancar tranzacție cu tranzacție, ci printr-o decontare periodică agregată de la procesatorul de plăți, care cumulează toate tranzacțiile POS ale zilei sau perioadei. Verificarea acestei decontări față de raportul POS și facturile emise are limite clare în motorul de matching automat.

## Temeiul legal

::: ghid-temei
**Articolul 6 (1)** Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ.

**29. - (2)** Disponibilitățile aflate în conturi la bănci [...] se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității. [...]
:::

## De ce decontarea POS nu se potrivește automat

Motorul de matching identifică facturile unui partener pe baza CUI-ului din descrierea liniei bancare. O decontare POS conține, de regulă, textul procesatorului ("DECONTARE POS") și suma netă agregată a tuturor tranzacțiilor cu cardul din perioadă, nu CUI-ul fiecărui client care a plătit cu cardul. Fără CUI, linia primește automat status roșu, indiferent de câte tranzacții individuale acoperă real suma decontată.

Verificarea corectă presupune compararea manuală a raportului POS (numărul și suma tranzacțiilor din ziua respectivă, emis de procesator sau de terminalul POS) cu suma decontată în extrasul bancar — și, separat, confruntarea soldurilor de cont conform textului legal citat mai sus. Diferența dintre suma brută din raportul POS și suma netă decontată provine de regulă din comisionul reținut de procesator, care trebuie contabilizat distinct.

## Ce se greșește în practică

- Se așteaptă ca motorul de matching să lege automat decontarea POS de facturile de vânzare cu amănuntul emise în ziua respectivă — fără CUI, motorul nu poate face această legătură.
- Se contabilizează suma netă decontată direct ca venit, fără separarea comisionului de procesare ca cheltuială distinctă.
- Se ignoră decalajul de una sau mai multe zile lucrătoare între data tranzacției POS și data decontării efective în cont.
- Se compară suma decontată direct cu totalul zilnic din casa de marcat, fără să se țină cont că raportul POS și raportul de casă pot include și alte mijloace de plată.

## Ce face iConta.eu

Motorul de matching (`core/reconciliere.py`) cere un CUI identificat pentru fiecare linie de extras. Liniile de decontare POS, fără CUI individual în descriere, primesc automat status roșu, alocări goale, motiv "fără CUI în descriere". Pentru aceste linii, sistemul poate propune o sugestie de cont pe baza istoricului deja contat de utilizator, fără nicio bază legală atribuită.

Verificarea decontării POS față de raportul POS și facturile emise rămâne un pas manual, în afara ariei acestui motor de matching pe CUI și factură.

[iConta.eu](/)
