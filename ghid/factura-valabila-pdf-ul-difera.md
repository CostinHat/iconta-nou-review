---
title: "Care factură este valabilă dacă PDF-ul diferă de XML-ul din e-Factura?"
description: "Legal câștigă XML-ul semnat electronic de Ministerul Finanțelor; tehnic, o diferență de bani între PDF și XML poate apărea din cauza rotunjirii, nu doar din eroare umană."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care factură este valabilă dacă PDF-ul diferă de XML-ul din e-Factura?

Dacă observi o sumă diferită între PDF-ul facturii și XML-ul transmis prin RO e-Factura, întrebarea are un răspuns legal clar și, în plus, o cauză tehnică reală care poate explica de ce apare diferența la aceeași factură.

## Temeiul legal

::: ghid-temei
„Exemplarul original al facturii electronice se consideră fişierul de tip XML însoţit de semnătura electronică a Ministerului Finanţelor."
— OUG 120/2021 (RO e-Factura), art. 4 alin. (6) (sursă: anaf_surse/oug_120_2021.txt)
:::

- Legea desemnează XML-ul semnat electronic de Ministerul Finanțelor drept exemplarul original al facturii electronice — nicio altă variantă (PDF, tipărit, capturi de ecran) nu are acest statut.
- Pentru operațiunile dintre firme stabilite în România, doar factura care respectă condițiile RO e-Factura e „considerată factură" în sensul legii (Codul fiscal, art. 319 alin. (1^1)) — deci XML-ul câștigă întotdeauna în fața unei variante PDF divergente, indiferent de motivul divergenței.

## Ce se greșește în practică

- Se presupune că o diferență de bani între PDF și XML e o eroare de introducere a datelor și se refac manual calculele, în loc să se verifice mai întâi dacă sursa e aceeași.
- Se ia ca reper suma din PDF (pentru că „arată mai clar"), deși XML-ul e cel valabil legal.
- Nu se verifică dacă diferența apare constant, la anumite prețuri (cu multe zecimale), semn că problema e la nivel de rotunjire, nu de date.

## Ce face iConta.eu

Aici există și o cauză tehnică reală, verificată în codul aplicației: cele două generatoare rotunjesc sumele diferit. PDF-ul (`core/pdf_util.py::bani`) rotunjește fără să specifice explicit metoda de rotunjire, ceea ce face ca Python să folosească implicit rotunjirea bancară (ROUND_HALF_EVEN). XML-ul pentru e-Factura (`core/efactura_send.py::_bani`) rotunjește explicit cu ROUND_HALF_UP — regula standard folosită de aplicație pentru sumele fiscale.

Exemplu reprodus direct din calcul: pentru 3 bucăți la 3,335 lei/bucată, baza de calcul e 10,005 lei. Rotunjită implicit (stilul din PDF), rezultă **10,00 lei**; rotunjită cu ROUND_HALF_UP (stilul din XML), rezultă **10,01 lei** — o diferență reală de un bănuț, din exact aceleași date sursă, nu o eroare de introducere. La facturi cu multe linii, astfel de diferențe se pot cumula pe subtotalul pe cotă de TVA sau pe total.

Este un defect confirmat în cod, nu reparat la data acestui ghid. Dacă vezi o astfel de diferență, suma valabilă e cea din XML (verificabilă în portalul SPV/ANAF), nu cea din PDF.

[iConta.eu](/)
