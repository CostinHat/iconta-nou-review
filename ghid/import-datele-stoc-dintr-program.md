---
title: "Cum import datele de stoc dintr-un program în balanță"
description: "Ce cere legea contabilității când datele de stoc vin dintr-un alt program și trebuie regăsite corect în balanța de verificare, conform Legii 82/1991."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum import datele de stoc dintr-un program în balanță

Trecerea de la un program de gestiune la altul, sau simpla preluare a soldurilor de stoc dintr-o aplicație separată de facturare, ridică o singură întrebare cu adevărat importantă din punct de vedere legal: soldurile importate se regăsesc corect, pe conturi, în balanța de verificare lunară.

## Temeiul legal

::: ghid-temei
„Articolul 22 Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare.
Articolul 23 (1) Persoanele prevăzute la art. 1 care utilizează sisteme informatice de prelucrare automată a datelor au obligația să asigure prelucrarea datelor înregistrate în contabilitate în conformitate cu reglementările contabile aplicabile, controlul și păstrarea acestora pe suporturi tehnice timp de 5 ani calculați de la data de 1 iulie a anului următor celui încheierii exercițiului financiar în care au fost întocmite."
— Legea contabilității nr. 82/1991, art. 22 și art. 23 alin. (1) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce rezultă pentru un import de date de stoc:

- **Obligația de fond** nu e despre formatul fișierului importat, ci despre rezultat: după import, **balanța de verificare lunară trebuie să reflecte corect** soldurile de stoc pe conturile de materii prime, materiale, mărfuri etc. (art. 22).
- Firma care folosește un sistem informatic pentru prelucrarea datelor **răspunde pentru corectitudinea prelucrării**, indiferent din ce sursă provin datele — un import dintr-un alt program nu mută răspunderea către acel program, ci rămâne obligație a entității (art. 23 alin. (1)).
- Datele prelucrate informatic trebuie **păstrate pe suporturi tehnice** timp de 5 ani de la 1 iulie a anului următor încheierii exercițiului — inclusiv fișierele sursă ale importului, ca probă a modului în care s-au constituit soldurile.

## Ce se greșește în practică

- Se importă cantitățile fără valoare (sau invers), lăsând balanța dezechilibrată pe conturile de stocuri — importul e considerat "gata" doar dacă se verifică efectiv soldul rezultat în balanță, nu doar reușita tehnică a fișierului.
- Se importă soldul de stoc fără să se verifice metoda de evaluare folosită de sursă (CMP, FIFO, preț standard) — un import care schimbă metoda de evaluare fără documentarea motivului încalcă cerința de consecvență a metodei contabile.
- Nu se păstrează fișierul sursă al importului — la un control ulterior, fără el, nu se poate reconstitui modul în care s-a ajuns la soldul din balanță.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă un importator de articole și stoc inițial expus utilizatorului: `core/articole_import_api.py` citește un export .xlsx/.csv (denumire, UM, cantitate, preț unitar, cont de stoc) și creează articolele plus intrarea inițială pentru cele cu stoc, la data soldului declarată; funcția refuză explicit un articol cu stoc dar preț zero/lipsă, ca să nu subraporteze tăcut valoarea stocului. Fluxul e expus prin ruta `/tenants/{tenant_id}/articole-import` (`core/uc_tenants.py`), deci nu e un instrument doar intern de onboarding. `core/migrare_punte_stoc.py` și `core/migrare_stoc_lot4.py` sunt migrări de schemă (ALTER TABLE, coloane noi), nu importatoare de date de stoc, și nu trebuie confundate cu funcția de import de mai sus.

[iConta.eu](/)
