---
title: "Cum corectez soldurile inițiale preluate greșit în anul următor?"
description: "Cum se corectează o balanță de deschidere importată greșit, și de ce echilibrul debit-credit nu garantează singur corectitudinea soldurilor."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez soldurile inițiale preluate greșit în anul următor?

O balanță de deschidere greșită pornește toată contabilitatea anului pe un fundament greșit — orice sold ulterior se calculează pornind de la ea. Corectarea nu înseamnă „ajustarea" unui cont izolat, ci reluarea procesului de preluare cu date verificate.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. (2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea nr. 82/1991 (legea contabilității), art. 6 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Soldurile inițiale, ca orice altă înregistrare contabilă, trebuie să aibă la bază un document justificativ real — de regulă, balanța de închidere a exercițiului anterior, verificată. Câteva reguli practice pentru corectare:

- **Balanța de deschidere trebuie să aibă totalul debitor egal cu cel creditor** — orice diferență, oricât de mică, arată o eroare de preluare, nu doar o rotunjire.
- O balanță **fără solduri reale** (toate coloanele debit/credit la zero) nu e o balanță validă, chiar dacă „se echilibrează" formal pe 0=0 — semn că fișierul greșit a fost încărcat, nu balanța corectă.
- Conturile analitice din balanța de deschidere (clienți, furnizori individualizați) trebuie să existe în planul de conturi al firmei — o balanță cu analitice noi, neintrate în nomenclator, lasă solduri „orfane".
- Corectarea unei preluări greșite înseamnă, de regulă, **reimportarea balanței corecte**, care înlocuiește integral soldurile greșite anterioare — nu o ajustare punct cu punct a fiecărui cont afectat.

## Ce se greșește în practică

- Se corectează manual, cont cu cont, o balanță de deschidere greșit importată, în loc să se reia importul cu fișierul corect, verificat.
- Se validează o balanță doar pe baza faptului că debit=credit, fără să se observe că ambele sunt zero — un „echilibru" fals care ascunde un fișier gol sau greșit.
- Se ignoră conturile analitice care nu există încă în planul de conturi al firmei, iar soldurile aferente rămân neclasificate corect.

## Ce face iConta.eu

iConta.eu verifică, la importul soldurilor inițiale, ca totalul debitor să fie egal cu totalul creditor și respinge fișierele fără solduri reale sau fără conturi contabile recognoscibile — o balanță „goală" nu mai poate trece drept validată. Corectarea unei preluări greșite se face prin reimportarea balanței corecte, care înlocuiește integral soldurile anterioare (ștergere și reinserare), iar conturile analitice noi din balanță intră automat în planul de conturi al firmei.

[iConta.eu](/)
