---
title: "Cum se raportează produsele finite în SAF-T?"
description: "Secțiunea Stocuri din SAF-T (D406), inclusiv producția în curs, se raportează doar la solicitarea expresă a organelor fiscale — nu periodic."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează produsele finite în SAF-T?

Fișierul standard de control fiscal (SAF-T), depus prin Declarația informativă D406, are o secțiune dedicată „Stocuri", care acoperă și stocurile de produse finite și producția în curs. Spre deosebire de restul declarației D406, această secțiune nu se depune periodic (lunar/trimestrial), ci doar la cerere. Iată exact ce spune norma.

## Temeiul legal

::: ghid-temei
„9. Informațiile privind «stocurile de produse» și «producție în curs» sunt transmise pe baza unei solicitări specifice din partea organelor fiscale centrale. În funcție de perioada pentru care se solicită furnizarea informațiilor privind stocurile prin fișierul standard de control fiscal (SAF-T), contribuabilii furnizează una sau mai multe declarații informative cuprinzând subsecțiunile din fișierul SAF-T relevante pentru «Stocuri» [...] 10. Declarațiile informative D406 pentru «Stocuri» se depun în termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării."
— OPANAF nr. 1.783/2021, Anexa 4, pct. 9-10 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Câteva precizări utile despre acest mecanism:

- Secțiunea „Stocuri" din SAF-T (care include atât produsele finite, cât și producția în curs de execuție) **nu se raportează automat** odată cu restul declarației D406, ci doar dacă organul fiscal central o solicită expres.
- Termenul de depunere, odată solicitat, este de **minimum 30 de zile calendaristice** de la data cererii — stabilit de organul fiscal, nu unul fix, general valabil.
- Solicitarea poate viza una sau mai multe perioade (luni/trimestre) distincte, iar contribuabilul depune câte o declarație separată pentru fiecare.

## Ce se greșește în practică

- Se așteaptă ca secțiunea „Stocuri" să apară automat, lunar, alături de restul secțiunilor D406 — de fapt, ea se declanșează doar la solicitare.
- Nu se pregătește dinainte structura de date pentru stocuri (loturi, depozite, mișcări), iar la solicitare cele minimum 30 de zile se dovedesc insuficiente pentru o reconstituire manuală.
- Se confundă evidența contabilă a produselor finite (conturile 345/348/711) cu structura tehnică de raportare SAF-T pentru stocuri, care cere alte date (cod articol, depozit, cantități, mișcări), nu solduri contabile.

## Ce face iConta.eu

Aici e important să fim onești: mecanismul din spatele acestui ghid — notele contabile pentru producție (`345 = 711`, `331 = 711`, diferențele pe 348) — **nu este conectat** la raportarea SAF-T. Notele generate la obținerea produselor finite scriu exclusiv linii contabile în registrul de note; ele **nu populează** nicio structură de tip „articole" sau „mișcări de stoc" din care se construiește secțiunea „Stocuri" a SAF-T.

Raportarea SAF-T de stocuri este o funcționalitate separată în iConta.eu, care citește datele dintr-un modul dedicat de gestiune a stocurilor (alimentat de ecranele de facturare, rețete și import articole), complet independent de operațiunile de producție descrise aici. Cu alte cuvinte: un produs finit obținut printr-o notă de producție **nu apare automat** în raportul SAF-T de stocuri al iConta.eu — cele două funcții trăiesc separat în aplicație, la fel cum, conform normei de mai sus, și obligația de raportare a stocurilor e separată (la cerere) de restul declarației D406.

[iConta.eu](/)
