---
title: Cum aleg codul corect de scutire pentru factura electronică?
description: Codul de motiv al scutirii (VATEX) e o convenție tehnică a standardului european UBL/EN16931, nu o normă fiscală românească — și, la acest moment, iConta.eu nu generează niciun asemenea cod în XML-ul de e-Factura.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum aleg codul corect de scutire pentru factura electronică?

Înainte de „cum aleg", răspunsul cinstit e „nu poți alege încă din iConta.eu" — aplicația nu are, la acest moment, un asemenea câmp. Explicăm mai jos ce e de fapt codul respectiv și de ce nu-l putem prezenta ca funcționalitate existentă.

## Temeiul legal

::: ghid-temei
**Art. 319 alin. (20) lit. l) din Codul fiscal**: „în cazul în care este aplicabilă o scutire de taxă, trimiterea la dispozițiile aplicabile din prezentul titlu ori din Directiva 112 sau orice altă mențiune din care să rezulte că livrarea de bunuri ori prestarea de servicii face obiectul unei scutiri.”
:::

Legea românească cere mențiunea (temeiul scutirii), nu un cod tehnic anume. Codul de care se vorbește de obicei în context de e-Factura — cunoscut ca **VATEX** — e o listă de coduri din specificația tehnică europeană EN16931/UBL, pe care se bazează formatul CIUS-RO folosit de RO e-Factura. Nu am identificat, în sursele oficiale ANAF disponibile, un act normativ românesc care să stabilească separat această listă — ea vine din standardul tehnic european, nu din legea fiscală de la noi.

## Ce înseamnă practic

Un cod VATEX indică, în XML, motivul tehnic al scutirii (de exemplu: scutire pentru livrare intracomunitară, scutire pentru export, scutire pentru operațiuni în regim special etc.). Alegerea codului corect depinde de tipul exact al operațiunii, iar eroarea tipică e alegerea unui cod „apropiat", fără o verificare atentă a definiției lui exacte în specificație — dar acest lucru privește completarea manuală a XML-ului, nu un flux disponibil în iConta.eu.

## Ce se greșește în practică

Se caută un temei legal românesc pentru un anumit cod VATEX — nu există unul, pentru că lista e o convenție tehnică europeană, nu o normă fiscală. Ce trebuie verificat legal e mențiunea de scutire cerută de art. 319 alin. (20) lit. l), nu codul tehnic în sine.

## Ce face iConta.eu

De spus clar, fără ambiguitate: generatorul de XML pentru e-Factura al iConta.eu nu produce, la acest moment, niciun cod de motiv al scutirii (nu există, în cod, vreun câmp „VATEX", „motiv scutire" sau echivalent). Categoria de TVA din XML se stabilește exclusiv din cota facturii — standard sau cotă zero — fără nicio selecție de cod de scutire disponibilă în interfață. Dacă activitatea ta implică frecvent operațiuni scutite care cer explicit acest cod în XML, aceasta e, la acest moment, o limitare reală a aplicației, nu o opțiune ascunsă undeva în ecranul de facturi.

[iConta.eu](/)
