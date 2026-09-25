---
title: "Cheltuielile cu energia electrică sunt deductibile?"
description: "Regula generală de deductibilitate a cheltuielilor cu utilitățile — energie electrică inclusă — la impozitul pe profit și la TVA, și limitele ei în spațiile cu folosință mixtă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cheltuielile cu energia electrică sunt deductibile?

Nu există o listă separată, în Codul fiscal, cu „cheltuieli cu energia electrică deductibile" — energia electrică se supune regulii generale de deductibilitate aplicabile oricărei cheltuieli: legătura cu activitatea economică. Cât timp firma poate demonstra această legătură, cheltuiala e deductibilă; când legătura lipsește sau e parțială, deductibilitatea se limitează corespunzător.

## Temeiul legal

::: ghid-temei
„(1) Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cheltuielile efectuate în scopul desfășurării activității economice, inclusiv cele reglementate prin acte normative în vigoare, precum și taxele de înscriere, cotizațiile și contribuțiile datorate către camerele de comerț și industrie, organizațiile patronale și organizațiile sindicale."
— Legea 227/2015 (Codul fiscal), art. 25 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă acest principiu general aplicat facturii de curent:

- **Testul e scopul cheltuielii, nu natura ei** — energia electrică nu e menționată explicit în lege ca „deductibilă" sau „nedeductibilă"; ea intră automat la deductibile dacă e consumată în scopul activității economice a firmei (sediu, punct de lucru, echipamente de producție etc.).
- **Dreptul de deducere a TVA urmează aceeași logică**, la art. 297 alin. (4) lit. a) din Codul fiscal — taxa aferentă achizițiilor (inclusiv energie electrică) e deductibilă în măsura în care achiziția e destinată operațiunilor taxabile ale firmei.
- **Problema reală apare la spațiile cu folosință mixtă** — un sediu social găzduit la domiciliul asociatului, de exemplu, ridică întrebarea cât din consumul total e de fapt aferent activității economice și cât e consum personal, iar doar partea aferentă activității rămâne deductibilă.
- **Refacturarea utilităților** (când chiriașul plătește proprietarului contravaloarea consumului) nu schimbă principiul — cheltuiala rămâne deductibilă la cel care o suportă efectiv, în scopul activității sale, indiferent cine e titularul contractului cu furnizorul de energie.

## Ce se greșește în practică

- Se deduce integral factura de curent a unui spațiu cu folosință mixtă (locuință + sediu de firmă), fără nicio justificare a proporției aferente activității economice — la un control, absența unei chei de repartizare documentate (suprafață, ore de utilizare) face vulnerabilă întreaga deducere.
- Se presupune că orice cheltuială „reglementată prin acte normative" (cum sugerează partea a doua a art. 25 alin. (1)) e automat deductibilă indiferent de legătura cu activitatea — condiția de bază, scopul economic, rămâne obligatorie.
- Se confundă deductibilitatea la impozitul pe profit cu dreptul de deducere a TVA — sunt două teste separate, aplicate fiecăruia dintre cele două impozite, chiar dacă folosesc aceeași logică generală.
- Se omite documentarea refacturării utilităților între chiriaș și proprietar, ceea ce lasă cheltuiala fără suport clar la niciuna dintre cele două părți.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un modul dedicat pentru refacturarea utilităților în relația comodat/chirie (`core/comodat_chirii.py`, funcția `nota_refacturare()`), care generează nota contabilă pentru partea din factura furnizorului de utilități refacturată către chiriaș/comodatar. Aplicația nu are însă o funcție care să calculeze automat proporția deductibilă a unei facturi de energie electrică pentru un spațiu cu folosință mixtă (locuință + sediu) — determinarea cheii de repartizare (suprafață, timp de utilizare) și justificarea ei documentată rămân, la acest moment, în sarcina contabilului.

[iConta.eu](/)
