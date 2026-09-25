---
title: "ANAF poate veni în control fără aviz"
description: "În ce situații organul fiscal poate efectua inspecție fiscală fără avizul prealabil de 15 sau 30 de zile, și ce e controlul inopinat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# ANAF poate veni în control fără aviz

Regula generală e că inspecția fiscală se anunță din timp, printr-un aviz de inspecție fiscală. Dar legea prevede și excepții exprese, în care avizul se comunică abia la începerea controlului sau nu se comunică deloc — cel mai cunoscut caz fiind controlul inopinat, care prin definiție se face fără înștiințare prealabilă.

## Temeiul legal

::: ghid-temei
„(4) Avizul de inspecție fiscală se comunică la începerea inspecției fiscale în următoarele situații: a) în cazul efectuării unei inspecții fiscale la un contribuabil/plătitor aflat în procedura de insolvență; b) în cazul în care, ca urmare a unui control inopinat, se impune începerea imediată a inspecției fiscale; c) pentru extinderea inspecției fiscale la perioade sau creanțe fiscale, altele decât cele cuprinse în avizul de inspecție fiscală inițial; d) în cazul refacerii inspecției fiscale ca urmare a unei decizii de soluționare a contestației; e) în cazul unor cereri ale contribuabilului/plătitorului pentru a căror soluționare, ca urmare a analizei de risc, este necesară efectuarea inspecției fiscale."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 122 alin. (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- **Regula generală**: avizul de inspecție fiscală se comunică înainte de începerea controlului — cu 30 de zile pentru marii contribuabili, cu 15 zile pentru ceilalți (art. 122 alin. (2)).
- **Excepțiile de la avizul prealabil** sunt limitativ enumerate: insolvență, extindere imediată în urma unui control inopinat, extinderea perioadelor/creanțelor controlate, refacerea inspecției după o contestație admisă, sau cereri ale contribuabilului care necesită inspecție conform analizei de risc.
- **Controlul inopinat e o instituție separată**, distinctă de inspecția fiscală: „Organul fiscal poate efectua un control fără înștiințarea prealabilă a contribuabilului/plătitor, denumit în continuare control inopinat" (art. 134 alin. (1)) — acesta nu are, prin natura lui, aviz prealabil, dar durata îi e limitată la maximum 30 de zile (art. 134 alin. (3)).

## Ce se greșește în practică

- Se presupune că orice control fără aviz prealabil e nelegal — legea prevede expres cazurile în care avizul se comunică ulterior sau nu se comunică deloc (controlul inopinat).
- Se confundă controlul inopinat cu inspecția fiscală propriu-zisă — sunt proceduri diferite, cu obiect și durată diferite, deși un control inopinat poate declanșa, în anumite condiții, o inspecție fiscală imediată.
- Se refuză colaborarea cu organul de control pe motiv de lipsă a avizului, fără verificarea prealabilă a legitimației și ordinului de serviciu, care rămân obligatorii indiferent de tipul de control.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu are un modul care să gestioneze procedura de control fiscal (control inopinat sau inspecție fiscală) — există module de alerte legate de control fiscal (`core/alerte_control_fiscal.py`, `core/control_fiscal_api.py`) care semnalează contabilului riscuri sau neconcordanțe interne, dar interacțiunea efectivă cu organul de control, inclusiv verificarea avizului sau a legitimației, rămâne în sarcina firmei și a contabilului.

[iConta.eu](/)
