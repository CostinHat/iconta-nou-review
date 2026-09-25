---
title: "Când e scadentă e-Factura pentru fiecare tip de operațiune"
description: "Termenul general de transmitere prin RO e-Factura este de 5 zile lucrătoare de la emitere, cu excepții pentru anumite tipuri de operațiuni care nu intră sub această obligație."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când e scadentă e-Factura pentru fiecare tip de operațiune

Termenul de transmitere a facturilor prin sistemul național RO e-Factura e unic — 5 zile lucrătoare — dar obligația în sine nu se aplică tuturor tipurilor de operațiuni la fel. Legea distinge între relația B2B, relația cu instituțiile publice (B2G) și câteva categorii de operațiuni scutite explicit de obligație.

## Temeiul legal

::: ghid-temei
„Termenul-limită pentru transmiterea facturilor prevăzute la alin. (1)-(3) în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită prevăzută pentru emiterea facturii la art. 319 alin. (16) din Legea nr. 227/2015."
— Legea 296/2023, art. LIX alin. (6) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

- Termenul de **5 zile lucrătoare** se calculează în două moduri, iar transmiterea trebuie să respecte pe cel mai apropiat: de la data efectivă a emiterii facturii, dar niciodată mai târziu de 5 zile lucrătoare de la data-limită legală de emitere a facturii (art. 319 alin. 16 Cod fiscal) — dacă factura nu e emisă la timp, ceasul curge oricum de la termenul legal de emitere.
- Obligația de transmitere prin RO e-Factura se aplică, potrivit art. LIX alin. (1)-(3): livrărilor de bunuri și prestărilor de servicii cu locul în România, în relația **B2B** dintre persoane impozabile stabilite în România; operațiunilor cu **instituții publice**, altele decât cele deja acoperite de relația B2G; și, de la 1 ianuarie 2024, operatorilor nestabiliți dar înregistrați în scopuri de TVA în România.
- Sunt **exceptate** de la obligație (art. LIX alin. 4): livrările scutite de TVA pentru export/livrări intracomunitare (art. 294 alin. 1 lit. a și b Cod fiscal); livrările/prestările către persoane care nu sunt nici stabilite, nici înregistrate în scopuri de TVA în România; facturile simplificate (art. 319 alin. 12 Cod fiscal); prestările de servicii pentru care emiterea facturii nu face obiectul normelor de facturare aplicabile în România (art. 319 alin. 5 Cod fiscal).
- Nerespectarea termenului de 5 zile lucrătoare, pentru facturile scadente într-o lună calendaristică, e sancționată contravențional, cu amenzi diferite pe categorie de contribuabil: 5.000-10.000 lei pentru contribuabilii mari, 2.500-5.000 lei pentru cei mijlocii și 1.000-2.500 lei pentru restul persoanelor juridice și pentru persoanele fizice (art. LIX alin. 7).

## Ce se greșește în practică

- Se presupune că fiecare tip de operațiune (B2B, B2G, export, servicii) are un termen de transmitere diferit — de fapt termenul e unic (5 zile lucrătoare), diferă doar dacă operațiunea intră sau nu sub obligația de raportare.
- Se calculează termenul strict de la data facturii, ignorând regula suplimentară care leagă termenul de data-limită legală de emitere a facturii, dacă aceasta a fost depășită.
- Se transmit prin RO e-Factura și operațiuni exceptate expres (de exemplu facturi simplificate sau livrări intracomunitare scutite), fără să se verifice lista de excepții de la art. LIX alin. (4).
- Se ignoră faptul că amenda pentru întârziere depinde de categoria de contribuabil (mare/mijlociu/altul), nu e o sumă fixă unică.

## Ce face iConta.eu

Aplicația are un modul complet de emitere și trimitere a facturilor prin RO e-Factura (integrare directă cu SPV — conector, poll și trimitere automată), pe care se bazează fluxul de facturare al utilizatorilor. Nu am găsit însă, în codul verificat, o verificare explicită a termenului legal de 5 zile lucrătoare sau o alertă automată de apropiere a scadenței de transmitere — monitorizarea încadrării în termen rămâne, la data acestui ghid, responsabilitatea utilizatorului.

[iConta.eu](/)
