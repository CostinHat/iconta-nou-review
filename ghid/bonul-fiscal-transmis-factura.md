---
title: "Bonul fiscal trebuie transmis în e-Factura?"
description: "Excepția pentru bonurile fiscale emise de casele de marcat de la obligația de transmitere a facturilor în sistemul RO e-Factura pentru vânzările către persoane fizice."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Bonul fiscal trebuie transmis în e-Factura?

Nu. De la 1 ianuarie 2025, comercianții trebuie să transmită prin sistemul RO e-Factura facturile emise către persoane fizice (relația B2C), dar legea a scos explicit bonurile fiscale de sub această obligație, atâta vreme cât acestea îndeplinesc condițiile unei facturi simplificate.

## Temeiul legal

::: ghid-temei
„Începând cu data de 1 ianuarie 2025, operatorii economici - persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015, [...] pentru livrările de bunuri și prestările de servicii care au locul livrării/prestării în România conform titlului VII «Taxa pe valoarea adăugată» din Legea nr. 227/2015, [...] efectuate în relația B2C, astfel cum este definită la art. 2 alin. (1) lit. n^1), au obligația să transmită facturile emise în sistemul național privind factura electronică RO e-Factura. Fac excepție bonurile fiscale emise în conformitate cu prevederile Ordonanței de urgență a Guvernului nr. 28/1999, republicată, cu modificările și completările ulterioare, care îndeplinesc condițiile unei facturi simplificate, în conformitate cu prevederile art. 319 alin. (12), (13) și (21) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— OUG 120/2021 privind Sistemul național privind factura electronică RO e-Factura, art. 10^1 alin. (2), astfel cum a fost modificat de OUG 138/2024, art. I pct. 3 (sursă: anaf_surse/oug_138_2024.txt)
:::

- Obligația de transmitere în RO e-Factura pentru relația B2C (livrări către persoane fizice care nu se identifică printr-un cod de identificare fiscală, sau care optează să se identifice prin CNP) e generală de la 1 ianuarie 2025, dar are o excepție explicită pentru bonurile fiscale.
- Excepția se aplică **doar** bonurilor fiscale emise conform OUG 28/1999 (legea aparatelor de marcat electronice fiscale) **care îndeplinesc condițiile unei facturi simplificate**, prevăzute de Codul fiscal la art. 319 alin. (12), (13) și (21) — practic, bonurile fiscale obișnuite emise de casa de marcat, sub pragul valoric al facturii simplificate.
- Motivul practic al excepției e că bonurile fiscale sunt deja transmise electronic către ANAF prin conexiunea caselor de marcat electronice fiscale (jurnalul electronic), deci raportarea lor separată prin RO e-Factura ar fi o dublă transmitere a acelorași date.
- Excepția vizează strict bonul fiscal ca atare — dacă vânzarea către o persoană fizică e documentată printr-o factură propriu-zisă (nu prin bon fiscal), acea factură intră sub obligația generală de transmitere în RO e-Factura pentru relația B2C.

## Ce se greșește în practică

- Se presupune că orice vânzare către persoane fizice trebuie raportată separat prin RO e-Factura, inclusiv cele documentate cu bon fiscal — deși legea exceptează explicit bonurile fiscale care îndeplinesc condițiile facturii simplificate.
- Se emit facturi (nu bonuri fiscale) pentru vânzări către persoane fizice și se omite transmiterea lor prin RO e-Factura, crezând că regula B2C s-ar aplica doar operatorilor cu casă de marcat.
- Se confundă transmiterea automată a datelor de la casele de marcat electronice fiscale către ANAF (prin jurnalul electronic, sub OUG 28/1999) cu sistemul RO e-Factura — sunt două canale de raportare diferite, iar excepția de la e-Factura nu înseamnă că bonul fiscal scapă de orice raportare către autorități.
- Se ignoră faptul că excepția e condiționată de încadrarea bonului fiscal în plafonul facturii simplificate — peste acel plafon, documentul emis nu mai poate fi doar un bon fiscal, ci trebuie să fie o factură completă, supusă regulilor obișnuite de transmitere.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are o funcție de recunoaștere automată (prin inteligență artificială) a bonurilor fiscale scanate, care le clasifică drept „bon fiscal" sau „chitanță" pentru înregistrarea cheltuielilor firmei, extrăgând articolele și TVA-ul aferent. Aplicația nu emite însă bonuri fiscale — acestea sunt generate de casele de marcat electronice fiscale ale comerciantului — și nu are un modul dedicat de gestionare a obligației de transmitere B2C prin RO e-Factura pentru facturile emise către persoane fizice; excepția descrisă mai sus rămâne o verificare pe care emitentul trebuie s-o facă la sursă, în funcție de tipul documentului emis.

[iConta.eu](/)
