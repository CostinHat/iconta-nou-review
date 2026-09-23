---
title: "Cum se reflectă facturile în SAF-T"
description: Cum ajung facturile de vânzare și achiziție în secțiunea SourceDocuments a SAF-T — linie cu linie, reconciliate cu antetul, cu codurile de TVA sensibile la dată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se reflectă facturile în SAF-T

Facturile de vânzare și achiziție ajung în SAF-T în secțiunea SourceDocuments — dar nu ca simple totaluri, ci linie cu linie, exact cum apar în evidența contabilă.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.

În structura aceleiași anexe, secțiunea SourceDocuments cuprinde Sales Invoices, Purchase Invoices, Payments, Movement of Goods și Asset Transactions.
:::

## Ce conține, concret, o linie de factură în SAF-T

Pentru fiecare factură, SourceDocuments nu preia un singur rând cu suma totală, ci liniile reale ale facturii — produs, cantitate, unitate de măsură, preț, descriere, cotă de TVA — reconciliate obligatoriu cu antetul facturii (totalurile de pe linii trebuie să corespundă cu totalul declarat în antet). Fiecare linie poartă și contul contabil și informația fiscală aferentă (AccountID și TaxInformation pe linie), nu doar la nivel de document.

Codul de TVA aplicat liniilor de livrare e sensibil la data facturii: de la 1 august 2025, Legea nr. 141/2025 a schimbat codurile de TVA pentru livrări, iar fișierul trebuie să aplice codul corect în funcție de dacă factura e emisă înainte sau după această dată.

## Ce se greșește în practică

- Se presupune că SAF-T raportează facturile ca sumă globală, similar unui jurnal de vânzări simplificat — de fapt fiecare linie de produs apare separat, cu toate atributele ei.
- Se ignoră reconcilierea antet-linii — o factură la care totalul liniilor nu corespunde cu antetul e o sursă tipică de erori de validare.
- Se aplică același cod de TVA la livrări indiferent de dată, deși Legea 141/2025 a schimbat codurile începând cu 1 august 2025.

## Ce face iConta.eu

iConta.eu emite facturile de vânzare și achiziție în SourceDocuments cu liniile reale, extrase direct din liniile facturii (cantitate, UM, preț, descriere, cotă), reconciliate obligatoriu cu antetul — nu o linie sintetică per factură. Codul de TVA pe livrări e aplicat în funcție de data facturii (coduri diferite înainte/după 1 august 2025, conform Legii 141/2025). Rămâne neacoperită, la stadiul curent, secțiunea Payments — codul de emitere există, dar lista de plăți nu e încă populată din sursă.

[iConta.eu](/)
