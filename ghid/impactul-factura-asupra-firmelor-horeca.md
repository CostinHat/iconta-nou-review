---
title: "Impactul e-Factura asupra firmelor din HoReCa 2026"
description: "Ce înseamnă obligativitatea facturării electronice pentru restaurante, hoteluri și cafenele, și cum se combină cu obligațiile de casă de marcat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Impactul e-Factura asupra firmelor din HoReCa 2026

Firmele din HoReCa au o particularitate față de alte sectoare: majoritatea vânzărilor lor merg către consumatori finali, prin bon fiscal, nu prin factură. Obligația e-Factura le privește însă în măsura în care emit facturi — inclusiv la cererea clientului sau pentru clienți persoane juridice (evenimente, cazare corporate, catering) — și înțelegerea corectă a limitei dintre bon fiscal și factură electronică e esențială ca să nu se dubleze sau să se omită raportări.

## Temeiul legal

::: ghid-temei
„(1) În relația comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, cu modificările și completările ulterioare, emitentul facturii electronice are obligația de transmitere a acesteia către destinatar utilizând sistemul național privind factura electronică RO e-Factura, cu respectarea prevederilor art. 4 alin. (1). Fac excepție facturile simplificate emise conform art. 319 alin. (12) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— Legea 296/2023, art. LXV, Secțiunea a 3-a, Capitolul IV, pct. 4 (modifică art. 10 alin. (1) din OUG 120/2021), în forma aplicabilă de la 1 iulie 2024 (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

Notă onestă: sursele consultate în `anaf_surse/` conțin regimul general al facturării electronice, dar **nu am găsit** un act normativ dedicat exclusiv sectorului HoReCa. Regulile generale relevante pentru HoReCa sunt:

- **Bonul fiscal** rămâne documentul standard pentru vânzarea către persoana fizică prin casa de marcat — e-Factura nu înlocuiește obligația de emitere a bonului fiscal la momentul vânzării.
- Când HoReCa emite **factură** (persoană juridică, la cerere, pentru cazare/evenimente), aceasta intră sub regimul general al facturării electronice obligatorii B2B/B2G aplicabil în România, prin sistemul RO e-Factura.
- SAF-T (D406) e o obligație distinctă de raportare periodică, care se extinde pe categorii de contribuabili (mari, mijlocii, mici) conform calendarului stabilit prin OPANAF 1783/2021 și actele lui de modificare, indiferent de domeniul de activitate.

## Ce se greșește în practică

- Se presupune că un bon fiscal emis prin AMEF trebuie transformat automat în factură electronică — cele două documente au regimuri diferite; bonul fiscal nu devine factură decât dacă se solicită explicit emiterea unei facturi pe baza lui.
- Se ignoră obligația de facturare electronică pentru facturile emise ocazional către firme (de exemplu, facturarea unui eveniment corporate), tratându-le ca pe restul vânzărilor cu amănuntul.
- Se confundă termenele SAF-T (D406) cu cele de e-Factura — sunt obligații separate, cu calendare și praguri de aplicare diferite.

## Ce face iConta.eu

La data acestui ghid, **nu am identificat în cod, prin cercetare directă, un modul specific etichetat pentru sectorul HoReCa**. Am găsit însă module generale relevante pentru orice firmă care emite facturi și declarații: `core/efactura_send.py`, `core/efactura_trimitere.py` și `core/efactura_import.py` (trimiterea și importul facturilor electronice prin SPV) și `core/d406.py` (generarea declarației SAF-T). Aceste module se aplică oricărei firme, inclusiv din HoReCa, în măsura în care emite facturi — dar aplicația nu are o logică separată pentru particularitățile HoReCa (bon fiscal vs. factură, gestiune de restaurant, bacșiș). Pentru bacșiș există modulul `core/bacsis.py`, cu evidența contabilă generală aferentă. Regimul concret aplicabil unei firme HoReCa rămâne responsabilitatea contabilului.

[iConta.eu](/)
