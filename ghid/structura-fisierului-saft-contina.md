---
title: "Structura fișierului SAF-T: ce trebuie să conțină"
description: Cele patru module ale fișierului SAF-T — Header, MasterFiles, GeneralLedgerEntries, SourceDocuments — și subsecțiunile lor, conform Anexei 1 la OPANAF 1783/2021.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Structura fișierului SAF-T: ce trebuie să conțină

Fișierul D406 nu e o listă de totaluri, ci o oglindă a evidenței contabile — structurată în module distincte, definite integral de schema oficială ANAF.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.
:::

## Cele patru module

Conform structurii Anexei 1 (pct. 4-5), fișierul SAF-T are patru module raportabile:

- **Header (Antet)** — datele de identificare ale declarantului și perioadei raportate.
- **MasterFiles** — nomenclatoarele: GeneralLedgerAccounts (conturi, tip, solduri), Customers, Suppliers, Tax Table, UOMTable, AnalysisType Table, MovementType Table, Products, PhysicalStock, Owners și Assets.
- **GeneralLedgerEntries** — mișcările din Registrul-jurnal.
- **SourceDocuments** — Sales Invoices, Purchase Invoices, Payments, Movement of Goods, Asset Transactions.

O precizare din aceeași anexă: secțiunea **Taxonomies** e exclusă explicit din structura raportabilă — nu se depune în D406, deși apare menționată în alte contexte ale schemei.

Nu toate componentele au aceeași frecvență de depunere. Raportarea periodică (Header + MasterFiles + GeneralLedgerEntries + majoritatea SourceDocuments) e lunară sau trimestrială. Secțiunea Active se depune separat, o singură dată pe an, la termenul situațiilor financiare. Secțiunea Stocuri (PhysicalStock) se depune doar la cererea explicită a ANAF, ca declarație independentă.

## Ce se greșește în practică

- Se crede că fișierul SAF-T conține doar facturi — de fapt, SourceDocuments e doar unul din patru module, alături de MasterFiles (nomenclatoare) și GeneralLedgerEntries (jurnalul contabil).
- Se depune secțiunea Taxonomies, considerând-o parte din declarație — Anexa 1 o exclude explicit din raportare.
- Se tratează Active și Stocuri ca părți ale raportării periodice lunare/trimestriale — sunt componente separate, cu ritm propriu.

## Ce face iConta.eu

iConta.eu generează Header, MasterFiles și GeneralLedgerEntries complet, conform schemei XSD. SourceDocuments (Sales/Purchase Invoices) se emite cu liniile reale de factură — produs, cantitate, unitate de măsură, preț, cotă — reconciliate obligatoriu cu antetul facturii. La stadiul curent, secțiunea Payments nu e populată (lipsă sursă de plăți), iar Movement of Goods și Asset Transactions rămân neacoperite (opționale în schema XSD). Secțiunea Active (anuală) are propriul generator, cu amortizare calculată pe metoda reală a fiecărui activ.

[iConta.eu](/)
