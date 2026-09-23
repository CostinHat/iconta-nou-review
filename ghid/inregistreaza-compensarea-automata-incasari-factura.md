---
title: Cum se înregistrează compensarea automată a unei încasări cu factura clientului?
description: Ce se numește adesea „compensare automată" e de fapt alocarea automată a unei încasări pe facturile deschise ale clientului — nu compensarea legală din Codul civil. Iată cum funcționează mecanismul din iConta.eu.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se înregistrează compensarea automată a unei încasări cu factura clientului?

În vorbirea curentă, „compensarea automată a unei încasări cu factura" descrie de regulă mecanismul prin care aplicația leagă singură o încasare bancară de factura pe care o stinge, fără intervenție manuală. Nu e vorba de compensarea legală reciprocă dintre o creanță și o datorie (Codul civil, art. 1616-1623) — pentru a evita confuzia terminologică, în acest ghid folosim „alocare automată", termenul mai exact pentru ce face de fapt motorul de reconciliere.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ."
— Legea contabilității nr. 82/1991, art. 6 alin. (1)
:::

::: ghid-temei
„Pentru determinarea taxei aferente încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, care devine exigibilă potrivit prevederilor alin. (3), fiecare încasare totală sau parțială se consideră că include și taxa aferentă."
— Codul fiscal (Legea 227/2015), art. 282 alin. (8)
:::

## Cum funcționează alocarea automată

Când se importă un extras bancar, fiecare linie de încasare e verificată, în ordine, pentru:

1. **Potrivire exactă cu o singură factură** a clientului identificat pe linie (după CUI) — dacă suma coincide (cu o toleranță de un ban) cu soldul unei facturi deschise, alocarea e automată.
2. **Potrivire exactă cu o combinație de 2-4 facturi** ale aceluiași client — dacă suma coincide exact cu suma soldurilor mai multor facturi.
3. **Alocare parțială**, pe facturile cele mai vechi ale clientului mai întâi, dacă nu există potrivire exactă — necesită confirmare manuală înainte de contabilizare.

Alocarea automată (verde, potrivire exactă) nu contabilizează singură nota — ea propune legătura încasare↔factură; contabilul confirmă din ecranul Bancă („Contează"), moment în care se creează nota contabilă (debit 5121/5124, credit 4111) și, dacă firma aplică TVA la încasare, se calculează automat și TVA-ul exigibil aferent sumei încasate.

## Ce se greșește în practică

- Se folosește termenul „compensare" pentru acest flux în comunicarea cu clientul sau în documentele interne, ceea ce poate crea confuzie cu o compensare legală reciprocă (creanță vs. datorie) — cele două sunt mecanisme diferite.
- Se presupune că alocarea automată contabilizează și ea singură nota, fără confirmare — de fapt, „Contează" rămâne un pas manual, chiar și pentru o potrivire exactă.
- Se ignoră faptul că, la TVA la încasare, fiecare alocare parțială generează propriul calcul de TVA exigibil, proporțional cu suma efectiv încasată prin acea linie.

## Ce face iConta.eu

Motorul de reconciliere (`core/reconciliere.py`) caută automat potrivirea exactă sau pe combinație de facturi ale clientului identificat pe linia de extras, iar contabilizarea efectivă (`core/reconciliere_api.py`) se face la confirmarea „Contează", cu formula debit 5121/5124, credit 4111. Dacă firma aplică TVA la încasare, TVA-ul exigibil se calculează automat, separat pentru fiecare alocare.

[iConta.eu](/)
