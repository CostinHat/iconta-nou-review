---
title: "Este PDF-ul facturii documentul fiscal oficial după transmiterea în e-Factura?"
description: "Pentru operațiunile dintre firme stabilite în România, documentul oficial este XML-ul semnat electronic de Ministerul Finanțelor, nu PDF-ul generat pentru vizualizare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Este PDF-ul facturii documentul fiscal oficial după transmiterea în e-Factura?

Răspuns scurt: nu. După ce o factură a fost transmisă și acceptată în sistemul RO e-Factura, documentul cu valoare juridică e fișierul XML semnat electronic de Ministerul Finanțelor, nu PDF-ul afișat sau descărcat pentru citire.

## Temeiul legal

::: ghid-temei
„Exemplarul original al facturii electronice se consideră fişierul de tip XML însoţit de semnătura electronică a Ministerului Finanţelor."
— OUG 120/2021 (RO e-Factura), art. 4 alin. (6) (sursă: anaf_surse/oug_120_2021.txt)
:::

- Legea leagă statutul de „exemplar original" strict de fișierul XML **și** de semnătura electronică a Ministerului Finanțelor aplicată pe el — nu de un document derivat, generat ulterior, în alt format.
- Pentru relațiile dintre persoane impozabile stabilite în România, Codul fiscal restrânge explicit domeniul: doar facturile care respectă condițiile RO e-Factura sunt „considerate facturi" în sensul legii:

> „Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 [...]"
> — Codul fiscal, art. 319 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
- Nu există în aceste texte o mențiune separată despre statutul juridic al unui PDF generat în paralel — concluzia că PDF-ul nu e documentul oficial e o deducție directă din faptul că legea numește explicit doar XML-ul, nu o afirmație literală „PDF-ul nu e valabil".

## Ce se greșește în practică

- Se arhivează doar PDF-ul facturii (trimis prin email sau descărcat din aplicație) și se șterge sau se ignoră XML-ul descărcat din SPV, considerându-l „redundant".
- Se prezintă PDF-ul ca probă la un control sau la o instanță, în loc de XML-ul semnat, descărcat din portalul ANAF/SPV.
- Se presupune că, odată ce factura apare „acceptată" în e-Factura, PDF-ul generat de aplicație capătă automat aceeași valoare juridică — nu există niciun mecanism, legal sau tehnic, care să facă asta.

## Ce face iConta.eu

Funcționalitatea „PDF factură" din iConta.eu (`core/factura_pdf.py`) generează un document de vizualizare: randare reportlab a datelor facturii, cu logo, culoare accent și font personalizabile ale firmei, folosit la emitere, pe portalul clientului și la trimiterea prin email. Acest PDF **nu e stocat** ca „versiune finală" a facturii și **nu are nicio legătură de cod** cu procesul de transmitere, validare și semnare din RO e-Factura — se generează din nou, la fiecare cerere, din datele curente ale facturii din baza de date.

Aplicația nu marchează nicăieri PDF-ul ca „neoficial" sau „copie" — nu există în interfață o distincție vizuală între PDF-ul unei facturi transmise prin e-Factura și al uneia care nu a fost. Statutul juridic descris mai sus rămâne o informație pe care contabilul trebuie s-o cunoască, nu una semnalată de aplicație.

[iConta.eu](/)
