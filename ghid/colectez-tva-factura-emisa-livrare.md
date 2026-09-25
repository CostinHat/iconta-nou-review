---
title: "Când colectez TVA dacă factura este emisă după livrare?"
description: "De ce exigibilitatea TVA rămâne legată de data livrării, nu de data facturii, atunci când factura e emisă ulterior faptului generator."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când colectez TVA dacă factura este emisă după livrare?

Ordinea normală — livrare, apoi factură — nu schimbă regula de bază a TVA. Exigibilitatea taxei rămâne legată de momentul livrării (faptul generator), chiar dacă factura a fost emisă câteva zile sau chiar săptămâni mai târziu, în limita termenului legal.

## Temeiul legal

::: ghid-temei
„(1) Exigibilitatea taxei intervine la data la care are loc faptul generator.
(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: a) la data emiterii unei facturi, înainte de data la care intervine faptul generator;"
— Legea nr. 227/2015 (Codul fiscal), art. 282 alin. (1), (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din text pentru cazul unei facturi emise după livrare:

- **Regula generală** (alin. (1)) este că TVA devine exigibilă la data faptului generator — de regulă, data livrării bunurilor sau a prestării serviciilor.
- **Excepția** de la alin. (2) lit. a) se aplică doar când factura e emisă **înainte** de faptul generator — în acel caz, exigibilitatea „sare" la data facturii. Când factura e emisă **după** livrare, excepția nu se activează: rămâne valabilă regula generală, iar TVA e exigibilă la data livrării, nu la data (ulterioară) a facturii.
- Practic, dacă o firmă livrează bunuri pe 28 ale lunii și emite factura abia pe 5 ale lunii următoare (în limita termenului legal de 15 zile din luna următoare), TVA aferentă acelei livrări e exigibilă și trebuie raportată în decontul lunii livrării (28), nu în decontul lunii facturii (5).
- Excepția de la sistemul TVA la încasare (alin. (3)) schimbă complet regula pentru firmele care au optat pentru acest sistem — la ele, exigibilitatea e legată de încasarea contravalorii, nu de faptul generator sau de data facturii; regula descrisă mai sus se aplică firmelor care NU au optat pentru TVA la încasare.

## Ce se greșește în practică

- Se raportează TVA în luna în care a fost emisă factura, nu în luna în care a avut loc efectiv livrarea, atunci când cele două date sunt în luni calendaristice diferite.
- Se presupune că excepția de la art. 282 alin. (2) lit. a) (exigibilitate la data facturii) se aplică oricărei facturi emise cu decalaj, indiferent dacă factura precede sau urmează livrării — deși excepția funcționează doar când factura e emisă înainte de faptul generator.
- Nu se verifică dacă firma aplică sistemul TVA la încasare, caz în care regula de mai sus nu se aplică deloc — exigibilitatea depinde de încasare, nu de livrare sau de factură.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează TVA colectată pe baza datelor introduse la emiterea facturii (`core/facturi.py`, `core/facturi_api.py`) și gestionează separat regimul TVA la încasare, acolo unde e aplicabil, prin modulele `core/cota_tva_incasare.py` și `core/tva_incasare.py` (funcția `tva_exigibil_alocari`). Pentru firmele care nu aplică TVA la încasare, corectitudinea raportării TVA în luna faptului generator — și nu în luna facturii, dacă acestea diferă — depinde de data introdusă manual ca dată a livrării/prestării la fiecare factură; aplicația nu deduce automat data faptului generator dintr-un alt document (aviz de expediție, proces-verbal de recepție) decât dacă aceasta e introdusă explicit de utilizator.

[iConta.eu](/)
