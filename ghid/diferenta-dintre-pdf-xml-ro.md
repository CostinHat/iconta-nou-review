---
title: "Care este diferența dintre PDF și XML în RO e-Factura?"
description: "PDF-ul facturii e o randare vizuală generată la cerere, în timp ce XML-ul semnat de Ministerul Finanțelor este exemplarul original al facturii electronice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este diferența dintre PDF și XML în RO e-Factura?

Multe firme cred că PDF-ul pe care îl primesc sau îl descarcă e „factura", iar XML-ul e doar un fișier tehnic pentru ANAF. Legal, e exact invers pentru operațiunile RO-RO, iar tehnic, cele două documente sunt generate de mecanisme complet separate.

## Temeiul legal

::: ghid-temei
„Exemplarul original al facturii electronice se consideră fişierul de tip XML însoţit de semnătura electronică a Ministerului Finanţelor."
— OUG 120/2021 (RO e-Factura), art. 4 alin. (6) (sursă: anaf_surse/oug_120_2021.txt)
:::

- Legea numește explicit **XML-ul** ca exemplar original al facturii electronice — nu vorbește deloc despre eventualele PDF-uri generate de aplicații terțe, cum e cel produs de iConta.eu.
- Pentru operațiunile dintre persoane impozabile stabilite în România, doar factura care respectă condițiile RO e-Factura are, legal, calitatea de „factură":

> „Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 [...]"
> — Codul fiscal, art. 319 alin. (1^1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

## Ce se greșește în practică

- Se trimite clientului doar PDF-ul, considerându-l „dovada" facturii, fără să se verifice că XML-ul a fost efectiv transmis, validat și semnat electronic de Ministerul Finanțelor prin SPV.
- Se presupune că PDF-ul și XML-ul sunt „aceeași factură în două formate" — practic, sunt două randări generate independent, care pot ajunge, tehnic, să difere ușor (vezi sumele rotunjite diferit, mai jos).
- La un control sau la o dispută cu ANAF, se prezintă doar PDF-ul, în loc de XML-ul descărcat din portalul SPV/ANAF, care este documentul cu valoare juridică.

## Ce face iConta.eu

iConta.eu generează cele două documente prin module de cod complet independente. PDF-ul (funcționalitatea descrisă aici) e produs de `core/factura_pdf.py`, folosind reportlab: e randat la cerere, de fiecare dată din datele curente ale facturii, personalizabil cu logo, culoare accent și font ale firmei — nu e stocat separat și nu e trimis niciodată către SPV. XML-ul e generat de un modul diferit (`core/efactura_send.py`), în structura UBL/CIUS-RO cerută de RO e-Factura, și e cel transmis, validat și semnat electronic.

Cele două module nu comunică între ele în cod — PDF-ul nu importă și nu citește nimic din generatorul XML, și invers. Practic, asta înseamnă că, deși cele două documente descriu aceeași factură din baza de date, ele sunt calculate separat, iar sumele afișate pot ajunge, în cazuri rare, să difere cu un bănuț (vezi ghidul dedicat comparării sumelor dintre PDF și XML).

[iConta.eu](/)
