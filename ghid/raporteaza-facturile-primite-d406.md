---
title: Cum se raportează facturile primite în D406?
description: Facturile primite se raportează în secțiunea PurchaseInvoices din SourceDocuments, cu linii reale per produs, reconciliate obligatoriu cu antetul.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează facturile primite în D406?

Ca și facturile emise, facturile primite fac parte din SourceDocuments — la subsecțiunea PurchaseInvoices — și urmează aceeași logică de raportare la nivel de linie de document, nu doar de total.

## Temeiul legal

::: ghid-temei
GeneralLedgerEntries, SourceDocuments (Sales Invoices, Purchase Invoices, Payments, Movement of Goods, Asset Transactions). — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5 (structura SAF-T).
:::

Structura SAF-T tratează facturile primite (Purchase Invoices) simetric cu cele emise: fiecare document este raportat cu liniile lui de detaliu, nu doar cu valoarea totală înregistrată în contabilitate.

## Ce se greșește în practică

Greșeala tipică este preluarea facturilor primite direct din nota contabilă de înregistrare (cu suma totală pe cont), în loc de detalierea reală pe produse/servicii, cantități și cote de TVA — ceea ce nu corespunde structurii cerute de secțiunea PurchaseInvoices.

## Ce face iConta.eu

Conform docstring-ului generatorului (`core/d406.py`, actualizat 03.08.2026): „SourceDocuments: SalesInvoices/PurchaseInvoices se emit cu LINII REALE pe produs din factura_linii (cantitate/UM/pret/descriere/cota), reconciliate OBLIGATORIU cu antetul; DUK-validate structural (reparat 27.07)." Pentru facturile primite, aceasta înseamnă preluarea liniilor reale ale facturii (cantitate, unitate de măsură, preț, descriere, cotă), reconciliate automat cu antetul, cu verificare structurală prin validatorul DUK.

Cotele de TVA de pe liniile facturilor primite urmează aceeași logică period-aware descrisă pentru livrări: codurile TaxCode se aplică în funcție de data facturii, ținând cont de schimbarea introdusă de Legea 141/2025 de la 1 august 2025.

La fel ca la facturile emise, rămâne o limită tehnică generală a secțiunii SourceDocuments: subsecțiunea Payments nu este încă populată (lipsă mapare a plăților din trezorerie) — facturile primite în sine sunt raportate complet, dar corelarea lor cu plățile efective către furnizori nu este încă emisă.

[iConta.eu](/)
