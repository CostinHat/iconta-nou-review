---
title: "Cum verific SAF-T cu gestiunea stocurilor?"
description: "Când se transmite secțiunea 'Stocuri' din D406 (SAF-T) și cum se verifică față de gestiunea internă a firmei, potrivit OPANAF 1783/2021."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific SAF-T cu gestiunea stocurilor?

Spre deosebire de restul fișierului standard de control fiscal (D406), care se depune lunar sau trimestrial din oficiu, secțiunea „Stocuri" din SAF-T are un regim aparte: nu se transmite automat, ci doar la solicitarea punctuală a organului fiscal. Verificarea ei presupune, deci, mai întâi să știi exact ce perioadă și ce nivel de detaliu ți se cere.

## Temeiul legal

::: ghid-temei
„9. Informațiile privind «stocurile de produse» și «producție în curs» sunt transmise pe baza unei solicitări specifice din partea organelor fiscale centrale. În funcție de perioada pentru care se solicită furnizarea informațiilor privind stocurile prin fișierul standard de control fiscal (SAF-T), contribuabilii furnizează una sau mai multe declarații informative cuprinzând subsecțiunile din fișierul SAF-T relevante pentru «Stocuri», separate pentru fiecare dintre lunile/trimestrele calendaristice cuprinse în perioada pentru care a fost trimisă solicitarea din partea organelor fiscale centrale.
10. Declarațiile informative D406 pentru «Stocuri» se depun în termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării."
— Ordinul președintelui A.N.A.F. nr. 1.783/2021, Instrucțiuni de completare D406, pct. 9-10 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Secțiunea **„Stocuri"** din D406 nu se depune periodic din oficiu — se generează și se transmite **doar când organul fiscal solicită explicit** acest lucru, pentru o perioadă anume.
- Odată primită solicitarea, termenul minim pentru depunere este de **30 de zile calendaristice**; organul fiscal poate acorda un termen mai lung, dar nu mai scurt.
- Fișierul cuprinde, potrivit structurii tehnice a SAF-T, detalii pe articol de stoc: cod de încadrare tarifară (NC), cantitate la început și la final de perioadă, valoarea stocului la început și la final de perioadă, precum și date despre proprietarii stocurilor — relevant pentru bunuri aflate în custodie sau consignație.
- Verificarea internă înainte de depunere înseamnă, în esență, confruntarea acestor cantități și valori din fișier cu **fișele de magazie/balanța analitică de stocuri** ținută în contabilitate pentru aceeași perioadă — orice diferență semnalează fie o eroare de generare SAF-T, fie o problemă reală de gestiune.

## Ce se greșește în practică

- Se generează secțiunea „Stocuri" din SAF-T periodic, din obișnuință, deși legea o cere doar la solicitare punctuală a organului fiscal.
- Se ignoră termenul minim de 30 de zile și se depune fișierul în grabă, fără verificare, doar ca să se respecte o dată-limită presupusă.
- Nu se confruntă cantitățile din SAF-T cu evidența de gestiune înainte de transmitere, riscând să se raporteze automat diferențe pe care organul fiscal le va observa oricum.
- Se omite raportarea corectă a proprietarilor stocurilor pentru bunuri în custodie/consignație, tratându-le ca stoc propriu.

## Ce face iConta.eu

iConta.eu are un modul dedicat generării secțiunii de stocuri pentru SAF-T (`d406_stocuri.py`), care calculează soldurile de mișcări pe perioada cerută (`solduri`) și construiește structura XML necesară (`xml_entry`, `xml_physical_stock`) direct din datele de gestiune ale firmei introduse în modulul de stocuri. Practic, aplicația generează fișierul din aceleași date pe care le folosește și pentru evidența internă de stoc, ceea ce elimină riscul unei discrepanțe „artificiale" între SAF-T și gestiune — dar depunerea rămâne condiționată, ca și în lege, de solicitarea explicită din partea ANAF.

[iConta.eu](/)
