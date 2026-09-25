---
title: "Factura fiscală vs factura electronică"
description: "De ce termenul „factură fiscală” nu mai apare în Codul fiscal actual și ce diferențiază, legal, o factură obișnuită de una transmisă prin RO e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Factura fiscală vs factura electronică

„Factura fiscală" e o expresie moștenită din vocabularul contabil mai vechi, dinainte de alinierea deplină la directivele europene de TVA. Codul fiscal actual nu mai folosește acest termen — vorbește doar despre „factură", cu regulile de la art. 319, și, separat, despre factura electronică transmisă prin sistemul RO e-Factura.

## Temeiul legal

::: ghid-temei
„(2) Sistemul naţional privind factura electronică RO e-Factura reprezintă ansamblul de [...]
Articolul 319 Facturarea"
— OUG 120/2021, art. 3 alin. (2), și Codul fiscal (Legea 227/2015), art. 319, titlu (sursă: anaf_surse/oug_120_2021.txt și anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce rezultă din structura legislativă actuală:

- **„Factura fiscală" nu mai e un termen legal** — nu apare ca atare în Codul fiscal (Legea 227/2015). Documentul justificativ pentru o operațiune economică se numește simplu „factură", reglementată integral prin art. 319 din Codul fiscal (conținut obligatoriu, termene de emitere, excepții pentru facturi simplificate).
- **Factura electronică**, în sensul RO e-Factura, nu e un tip diferit de document, ci **un canal de transmitere** — o factură emisă conform art. 319 din Codul fiscal, dar transmisă (obligatoriu, pentru anumite categorii de operațiuni) prin sistemul național reglementat de OUG 120/2021, în format XML standardizat (RO_CIUS), validat de ANAF.
- Practic: orice factură emisă corect e deja „factură" în sensul legii; devine, în plus, „factură electronică" atunci când e transmisă prin RO e-Factura — nu există o categorie separată, „factura fiscală", paralelă cu cele două.

## Ce se greșește în practică

- Se caută în lege o categorie distinctă „factură fiscală", diferită de „factură" — termenul e învechit și nu mai are corespondent explicit în Codul fiscal actual.
- Se tratează factura electronică drept un tip de document diferit de factura clasică, în loc de a o vedea ca aceeași factură, transmisă printr-un canal digital standardizat.
- Se presupune că orice document numit informal „bon" sau „chitanță" are aceeași valoare fiscală ca o factură emisă conform art. 319 — regimul lor legal e diferit.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **emite facturi conform art. 319 din Codul fiscal** și le transmite, acolo unde e obligatoriu, prin sistemul RO e-Factura (module `core/efactura_send.py`, `core/efactura_trimitere.py`), validate pe schema RO_CIUS curentă. Aplicația nu tratează „factura fiscală" ca o categorie separată, ci urmează terminologia actuală a legii: factură, transmisă sau nu prin canalul electronic.

[iConta.eu](/)
