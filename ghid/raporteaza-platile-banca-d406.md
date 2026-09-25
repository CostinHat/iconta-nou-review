---
title: "Cum se raportează plățile prin bancă în D406?"
description: "Secțiunea Payments din fișierul standard de control fiscal (SAF-T/D406) și cum se raportează metoda de plată, inclusiv plățile prin bancă, potrivit OPANAF 1783/2021."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează plățile prin bancă în D406?

Fișierul standard de control fiscal (SAF-T, depus prin D406) are o secțiune dedicată explicit plăților, separată de facturile de vânzare și de achiziție. Plățile prin bancă nu au însă un tratament special față de alte metode de plată — se raportează în aceeași structură, diferențiate doar printr-un cod de metodă.

## Temeiul legal

::: ghid-temei
„[Sub-secțiunea] Payments (Plăți) — Conţine detalii despre plăţi, precum perioada, ID-ul tranzacţiei, data tranzacţiei, descriere, liniile de plăţi etc."
— OPANAF 1783/2021, Instrucțiuni SAF-T/D406, secțiunea SourceDocuments (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce se poate confirma, cu onestitate, din structura oficială:

- Secțiunea **Payments** face parte din **SourceDocuments**, alături de SalesInvoices, PurchaseInvoices și Movement of Goods — e o secțiune distinctă, dedicată strict tranzacțiilor de plată/încasare, nu integrată în facturi.
- Fiecare plată raportată conține, potrivit descrierii oficiale, perioada, ID-ul tranzacției, data, o descriere și liniile de plată aferente — structura tehnică exactă (inclusiv câmpul care indică metoda de plată) e detaliată în schema XSD D406, nu reluată complet în textul narativ citat aici.
- Textul oficial disponibil **nu conține o secțiune separată sau instrucțiuni distincte** pentru „plăți prin bancă" față de alte metode (numerar, card, compensare) — toate tipurile de plăți se raportează prin aceeași sub-secțiune Payments, diferențiate prin codul de metodă de plată din nomenclatorul ANAF asociat schemei XSD.

## Ce se greșește în practică

- Se așteaptă o secțiune sau un fișier separat pentru plățile bancare, distinct de restul plăților — structura SAF-T le include pe toate în aceeași sub-secțiune Payments, diferența fiind doar codul de metodă asociat fiecărei tranzacții.
- Se omite completarea sub-secțiunii Payments considerând-o opțională, deși raportarea corectă a fișierului D406 presupune completarea acestei secțiuni ori de câte ori există tranzacții de încasare/plată în perioada raportată.
- Se raportează plățile fără un cod de metodă recunoscut de nomenclatorul ANAF, ceea ce poate duce la validarea fișierului cu metoda de plată implicită, nu cu cea reală a tranzacției.

## Ce face iConta.eu

Motorul D406 al iConta.eu (`core/d406.py`) mapează metoda de plată a fiecărei tranzacții la codul ANAF corespunzător prin funcția `payment_method_anaf` — termenii interni „vir", „virament", „transfer", „op", „banca" sunt recunoscuți și mapați la codul „03" (plată fără numerar), folosit implicit pentru majoritatea plăților prin bancă; o metodă necunoscută primește codul implicit „03", cu semnalarea explicită a valorii înlocuite, nu tacit. Secțiunea `<Payments>` a fișierului XML se generează doar dacă există plăți înregistrate pentru perioada raportată. Rămâne responsabilitatea contabilului să se asigure că metoda de plată e introdusă corect la nivelul fiecărei tranzacții din aplicație, pentru ca maparea la codul ANAF să reflecte realitatea.

[iConta.eu](/)
