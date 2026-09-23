---
title: "Cum corectez o încasare bancară atribuită clientului greșit?"
description: Mecanismul e identic celui pentru o plată alocată greșit — depinde dacă nota contabilă generată de reconciliere e încă ciornă sau a fost deja validată, iar corectarea e blocată după închiderea lunii contabile.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez o încasare bancară atribuită clientului greșit?

O încasare potrivită automat pe facturile unui alt client decât cel real se corectează diferit, în funcție de starea notei contabile generate — ciornă sau deja validată.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ." — Legea contabilității nr. 82/1991, art. 6 alin. (1)
:::

Legea nu descrie explicit un mecanism de „corectare a alocării automate" — regula generală e că orice operațiune trebuie să rămână trasabilă la documentul ei real; de aici necesitatea ca o corectare să rupă legătura greșită și să lege operațiunea de factura corectă, nu doar să șteargă urma alocării.

## Pașii de corectare

1. **Dacă nota generată e încă ciornă**: se șterge direct din jurnal. Ștergerea readuce automat linia de extras pe starea „potrivită", gata de realocare la clientul corect din ecranul Bancă.
2. **Dacă nota a fost deja validată**: ștergerea e refuzată (doar ciornele se pot șterge). Se folosește dezlegarea legăturii dintre notă și factura greșită — necesită rol de administrator al firmei și motiv obligatoriu. Factura clientului greșit redevine „deschisă" (neîncasată), dar linia de extras rămâne afișată drept „contată", fără buton automat de realocare — o notă nouă, corectă, trebuie creată manual din jurnal.
3. **Corectarea, pe oricare din cele două căi, e blocată dacă luna contabilă e deja închisă.**

## Ce se greșește în practică

- Se caută un buton de „mutare" a încasării de la un client la altul — nu există un asemenea mecanism direct; calea corectă e ștergerea (pe ciornă) sau dezlegarea (pe notă validată), urmată de o alocare nouă.
- Se dezleagă nota de la factura clientului greșit, dar se uită crearea notei corecte pentru clientul real — încasarea reală rămâne neînregistrată la clientul potrivit.
- Nu se verifică dacă exigibilitatea TVA la încasare a fost deja declanșată de contarea greșită, la firmele cu acest regim — corectarea alocării nu anulează automat efectul fiscal deja produs, care trebuie tratat separat.

## Ce face iConta.eu

iConta.eu distinge clar între o notă ciornă (ștergere directă, cu resetarea automată a stării liniei bancare) și o notă validată (dezlegare explicită, cu rol de administrator și motiv obligatoriu). Pentru firmele cu TVA la încasare, aplicația calculează automat linia de exigibilitate TVA în momentul contării — dacă alocarea inițială a fost greșită, corectarea ei prin dezlegare/realocare urmează același circuit descris mai sus, fără o cale separată „doar pentru TVA".

[iConta.eu](/)
