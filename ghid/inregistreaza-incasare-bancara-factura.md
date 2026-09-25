---
title: "Cum se înregistrează o încasare bancară fără factură?"
description: "Ce document justifică o încasare bancară fără factură emisă și cum tratează iConta.eu, prin motorul de reconciliere, o linie de extras pe care nu o poate potrivi automat cu o factură."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează o încasare bancară fără factură?

Nu orice sumă care intră în contul firmei corespunde unei facturi emise — pot fi restituiri, garanții, avansuri fără factură încă emisă, dobânzi, sau pur și simplu încasări pentru care nu există (sau nu mai există) un document de tip factură. Legea permite înregistrarea unor astfel de operațiuni direct pe baza extrasului de cont, ca document justificativ propriu.

## Temeiul legal

::: ghid-temei
„Pentru operațiunile economice pentru care [...] nu există obligația întocmirii facturii, înregistrarea în contabilitate a acestora se efectuează pe baza contractelor [...] și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: aviz de însoțire a mărfii, chitanță, dispoziție de plată/încasare, extras de cont bancar, notă de contabilitate etc. [...]"
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 25 (sursă: anaf_surse/omfp_2634_2015_anexa1_norme_generale.txt)
:::

Pe lângă acest temei, mai contează:

- **Extrasul de cont e document justificativ** al operațiunilor bancare în sensul general al legii contabilității: „Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ" (Legea 82/1991, art. 6 alin. (1)).
- Chiar dacă operațiunea nu are factură, ea tot trebuie **corect calificată** înainte de a fi înregistrată — o încasare fără factură poate fi, în funcție de natura ei reală, un avans de la client (419), o restituire de garanție, o dobândă (766) sau o eroare de plată a unui terț (462, până la clarificare) — nu se contabilizează automat pe venit doar pentru că a intrat în cont.

## Ce se greșește în practică

- Se așteaptă apariția unei facturi pentru orice sumă încasată, chiar și când operațiunea nu presupune, prin natura ei, emiterea uneia (garanție, avans fără obligație de facturare imediată, restituire).
- Se înregistrează suma direct pe venit (7xx) fără să se stabilească întâi natura reală a încasării — o eroare frecventă mai ales la sumele nete de comision sau la încasările cumulate pe mai mulți clienți.
- Se lasă linia de extras „neatribuită" la nesfârșit, în loc să se creeze o notă contabilă manuală care să o clarifice — riscul e ca soldul contului bancar din contabilitate să nu mai corespundă cu extrasul.

## Ce face iConta.eu

Motorul de reconciliere bancară (F073, `core/reconciliere.py`) încearcă întâi să potrivească automat fiecare linie din extras cu facturile deschise ale unui partener, identificat după CUI-ul din descrierea liniei. Când **nu găsește un CUI pe linia de extras**, statusul e direct **roșu** — linia nu e potrivită cu nicio factură și rămâne vizibilă ca atare pe ecranul „Bancă", indiferent dacă e o încasare cu adevărat fără factură sau doar o descriere neclară a băncii. La fel, dacă un CUI e detectat dar partenerul respectiv nu are nicio factură deschisă pe direcția cerută (încasare → facturi emise), linia rămâne tot roșie.

Pentru aceste linii, iConta.eu nu forțează o potrivire — contabilul creează o **notă contabilă manuală** din ecranul de Jurnal, folosind linia de extras ca sursă și calificând corect operațiunea (avans, restituire, dobândă, etc.), conform documentului justificativ real (extrasul de cont, eventual contractul aferent). O dată contată manual, linia rămâne asociată extrasului, dar nu trece prin motorul automat de potrivire pe factură — acela e rezervat exclusiv liniilor care corespund unor facturi deschise ale unui partener identificat.

[iConta.eu](/)
