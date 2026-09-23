---
title: Cum se raportează facturile emise în SAF-T?
description: Facturile emise se raportează în secțiunea SalesInvoices din SourceDocuments, cu linii reale per produs, reconciliate obligatoriu cu antetul.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează facturile emise în SAF-T?

Facturile emise fac parte din secțiunea SourceDocuments a D406, la subsecțiunea SalesInvoices, alături de facturile primite (PurchaseInvoices), plăți, mișcări de bunuri și tranzacții cu active.

## Temeiul legal

::: ghid-temei
GeneralLedgerEntries, SourceDocuments (Sales Invoices, Purchase Invoices, Payments, Movement of Goods, Asset Transactions). — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5 (structura SAF-T).
:::

Legea nu descrie un simplu "total de facturi" pe perioadă — SourceDocuments este gândită ca o listă de documente sursă, cu date de detaliu, nu doar cu sume agregate. Pentru facturile emise (Sales Invoices), aceasta înseamnă raportarea fiecărei facturi cu liniile ei, nu doar cu valoarea totală.

## Ce se greșește în practică

O greșeală comună este tratarea secțiunii SourceDocuments ca pe un rezumat centralizator (similar unui jurnal de vânzări cu totaluri lunare), în loc de o listă de documente cu detaliu la nivel de linie — cantitate, unitate de măsură, preț, descriere și cotă de TVA pentru fiecare produs/serviciu facturat.

## Ce face iConta.eu

Conform docstring-ului generatorului (`core/d406.py`, actualizat 03.08.2026): „SourceDocuments: SalesInvoices/PurchaseInvoices se emit cu LINII REALE pe produs din factura_linii (cantitate/UM/pret/descriere/cota), reconciliate OBLIGATORIU cu antetul; DUK-validate structural (reparat 27.07)." Concret, pentru facturile emise, fiecare linie de produs din factura reală (cantitate, unitate de măsură, preț, descriere, cotă) este preluată direct din datele facturii și reconciliată automat cu totalurile din antetul documentului, iar rezultatul e verificat structural cu validatorul DUK.

O limită de reținut, valabilă la nivelul întregii secțiuni SourceDocuments, nu doar pentru facturile emise: subsecțiunea **Payments** nu este încă populată în fișierul generat — codul de emitere există, dar procesul de extragere a datelor (`pull()`) nu preia încă plățile, din lipsa unei surse de mapare a trezoreriei (decizie de business în așteptare). Facturile emise în sine sunt raportate complet; ceea ce lipsește este corelarea lor cu plățile efective, ca secțiune separată.

[iConta.eu](/)
