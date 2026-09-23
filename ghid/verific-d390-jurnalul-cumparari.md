---
title: Cum verific D390 cu jurnalul de cumpărări?
description: Verificarea D390 nu citește un jurnal de cumpărări separat — sursa e tabelul de facturi, filtrat pe partener UE, corelat cu nota contabilă validată.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific D390 cu jurnalul de cumpărări?

Dacă te gândești la jurnalul de cumpărări ca la o sursă distinctă pe care aplicația o confruntă cu D390, precizarea e importantă: nu există, în controlul D390, o citire separată a unui „jurnal de cumpărări". Sursa e alta, deși pornește tot din facturi.

## Temeiul legal

::: ghid-temei
**Art. 325 din Codul fiscal (Legea 227/2015)** — obligația depunerii lunare a declarației recapitulative (D390), cu achizițiile intracomunitare taxabile (lit. d) și livrările intracomunitare scutite (lit. a).

**Art. 278 din Codul fiscal** — locul operațiunii și taxarea inversă pentru achizițiile intracomunitare de bunuri.

**OMFP 1802/2014** — reglementările contabile, temeiul distincției dintre o notă contabilă validată și una în ciornă.
:::

Verificarea D390 pornește direct din **tabelul de facturi**, filtrat după direcție (emise/primite) și după partenerul cu cod de TVA valid dintr-un alt stat membru UE — nu dintr-un raport intermediar de tip „jurnal de cumpărări". Fiecare factură intracomunitară e apoi corelată cu nota contabilă validată legată de ea.

Dacă aplicația are, separat, un ecran sau raport numit „jurnal de cumpărări", alimentat din aceleași facturi, corelarea conceptuală se poate face în discuție — dar mecanismul propriu-zis al controlului D390 nu tratează acel jurnal ca sursă distinctă de verificare. Sursa rămâne factura, cu nota validată legată de ea.

## Ce se greșește în practică

- Se caută în ecranul de control fiscal o comparație explicită cu un jurnal de cumpărări — controlul D390 nu funcționează pe acel raport ca sursă separată.
- Se presupune că o factură care apare corect în jurnalul de cumpărări e automat „acoperită" în verificarea D390 — verificarea cere, suplimentar, ca factura să aibă notă contabilă validată legată de ea, nu doar să existe ca înregistrare.
- Se ignoră direcția facturii (emisă/primită) atunci când se interpretează diferențele — livrările și achizițiile intracomunitare sunt tratate pe perechi separate (L/A), nu ca un total unic.

## Ce face iConta.eu

Pentru D390, aplicația citește direct facturile intracomunitare ale perioadei (filtrate pe direcție și pe partenerul UE), corelate cu nota contabilă validată legată de fiecare — nu interoghează separat un raport de tip jurnal de cumpărări sau jurnal de vânzări ca sursă de comparație.

Dacă ai deja un jurnal de cumpărări generat din aceleași facturi, cifrele ar trebui să coincidă conceptual cu ce compară controlul D390 — dar corelarea explicită, dacă apare o diferență, se face verificând factura și nota ei, nu jurnalul ca atare.

[iConta.eu](/)
