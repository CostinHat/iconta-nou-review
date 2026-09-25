---
title: "Comisioanele procesatorului de plăți la WooCommerce: cum se înregistrează?"
description: "Comisionul reținut de un procesator de plăți (Stripe, PayU, Netopia etc.) e o cheltuială deductibilă separată de vânzare — și un subiect pe care conectorul WooCommerce al iConta.eu nu-l atinge automat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Comisioanele procesatorului de plăți la WooCommerce: cum se înregistrează?

Când un client plătește online printr-un procesator de plăți (Stripe, PayU, Netopia, EuPlătesc etc.), banii care ajung efectiv în contul firmei sunt mai mici decât valoarea comenzii — diferența e comisionul reținut de procesator. Contabil, vânzarea și comisionul sunt două operațiuni distincte, nu una singură „netă".

## Temeiul legal

::: ghid-temei
„Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cheltuielile efectuate în scopul desfășurării activității economice, inclusiv cele reglementate prin acte normative în vigoare, precum și taxele de înscriere, cotizațiile și contribuțiile datorate către camerele de comerț și industrie, organizațiile patronale și organizațiile sindicale."
— Legea 227/2015 (Codul fiscal), art. 25 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula generală de deductibilitate e simplă: o cheltuială e deductibilă dacă e efectuată în scopul desfășurării activității economice — comisionul unui procesator de plăți online, perceput exact pentru a putea încasa contravaloarea vânzărilor, se încadrează direct aici.
- Comisionul nu se scade din venitul facturat — venitul din vânzare se înregistrează la valoarea integrală a facturii emise către client, iar comisionul se înregistrează separat, ca o cheltuială cu servicii bancare/financiare.
- Documentul care stă la baza înregistrării comisionului e, de regulă, extrasul de cont sau factura/raportul periodic emis de procesatorul de plăți, nu comanda din WooCommerce.

## Ce se greșește în practică

- Se înregistrează în contabilitate doar suma netă încasată în cont, fără să se evidențieze separat comisionul ca o cheltuială proprie — diferența „dispare" nedocumentat.
- Se presupune că factura emisă din comanda WooCommerce reflectă deja, cumva, comisionul procesatorului — cele două documente nu au nicio legătură automată.
- Se amână înregistrarea comisioanelor pentru că sunt sume mici per comandă, deși cumulat, pe un volum mare de comenzi, pot deveni o cheltuială semnificativă, deductibilă și demonstrabilă doar dacă e înregistrată corect.

## Ce face iConta.eu

Conectorul WooCommerce al iConta.eu citește exclusiv liniile de produse ale unei comenzi (`line_items`) pentru a genera factura de vânzare — **nu citește și nu atinge niciodată informații despre comisioane sau taxe de procesare a plății** (verificat exhaustiv în codul conectorului: niciun apel către datele de comisioane ale comenzii). Așadar, nu există o funcție dedicată acestui subiect: comisionul procesatorului de plăți trebuie introdus manual în contabilitate, ca orice altă cheltuială de servicii bancare/financiare, pe baza extrasului de cont sau a documentului emis de procesator, separat de factura de vânzare generată automat din comandă.

[iConta.eu](/)
