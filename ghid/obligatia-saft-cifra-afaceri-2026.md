---
title: "Obligația SAF-T după cifra de afaceri 2026"
description: "Datele de referință de la care diferite categorii de contribuabili au obligația de a depune SAF-T (D406), conform procedurii ANAF."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Obligația SAF-T după cifra de afaceri 2026

„După cifra de afaceri" este o simplificare frecventă, dar nu chiar exactă: obligația SAF-T (D406) se declanșează pe baza încadrării contribuabilului în categoria de mari, mijlocii sau mici contribuabili — o clasificare făcută de ANAF, care are la bază mai multe criterii, nu doar cifra de afaceri izolată.

## Temeiul legal

::: ghid-temei
„1.1. Obligaţia de transmitere a fişierului standard de control fiscal prin intermediul Declaraţiei informative D406 devine efectivă pentru fiecare categorie de contribuabili, astfel: [...]
d) pentru contribuabilii care nu sunt încadraţi la data de 31 decembrie 2021 în categoria marilor contribuabili sau a contribuabililor mijlocii, denumiţi generic contribuabili mici, şi care îşi păstrează această încadrare şi după data de 1 ianuarie 2022, obligaţia de depunere a Declaraţiei informative D406 începe de la data de 1 ianuarie 2025, care reprezintă data de referinţă pentru contribuabilii mici;
e) contribuabilii nerezidenţi înregistraţi doar în scop de TVA în România au obligaţia de depunere a Declaraţiei informative D406 începând cu data de referinţă pentru contribuabilii mici (1 ianuarie 2025)."
— OPANAF nr. 407/2025, modificând Anexa 5 la OPANAF nr. 1.783/2021 (sursă: anaf_surse/opanaf_407_2025_saft_d406.txt)
:::

Din procedura ANAF rezultă un calendar pe categorii, nu un prag unic de cifră de afaceri:

- **Marii contribuabili** raportează din 1 ianuarie 2022 (cei încadrați și în 2021) sau din 1 iulie 2022 (noii mari contribuabili).
- **Contribuabilii mijlocii** raportează din 1 ianuarie 2023.
- **Contribuabilii mici** — categoria reziduală, care include majoritatea IMM-urilor — raportează din **1 ianuarie 2025**, dată care rămâne data de referință și pentru 2026, pentru cei care nu au fost încadrați anterior în categoria mare/mijlocie.
- **Contribuabilii nerezidenți înregistrați doar în scopuri de TVA** în România intră sub aceeași dată de referință ca și contribuabilii mici, adică 1 ianuarie 2025.
- Anumite categorii sunt **exceptate integral** de la SAF-T, indiferent de mărime: PFA, întreprinderi individuale, întreprinderi familiale, cabinete individuale (avocați, notari, medici), instituții publice și alte forme fără personalitate juridică care țin contabilitate în partidă simplă.

Încadrarea unui contribuabil în categoria mare/mijlociu/mic este stabilită de ANAF prin propriile criterii de clasificare (nu doar cifra de afaceri, ci și alți indicatori de mărime), comunicate contribuabilului — sursele verificate pentru acest ghid nu conțin un prag numeric explicit de cifră de afaceri care să delimiteze singur categoriile.

## Ce se greșește în practică

- Se presupune că există un prag simplu de cifră de afaceri, ușor de calculat, de la care pornește obligația SAF-T — de fapt, criteriul legal este încadrarea într-o categorie de contribuabili stabilită de ANAF, nu un calcul propriu al cifrei de afaceri.
- Se ignoră faptul că o firmă care trece dintr-o categorie mai mică într-una mai mare (de exemplu, din mică în mijlocie) capătă obligația de la data de referință a noii categorii, nu de la data efectivă a schimbării încadrării.
- Se presupune că un PFA cu cifră de afaceri mare intră automat sub obligația SAF-T — PFA-urile sunt exceptate explicit, indiferent de mărimea activității, cu excepția celor care optează pentru partidă dublă.

## Ce face iConta.eu

Pentru firmele care intră sub obligația SAF-T, iConta.eu generează Declarația D406 din propriile registre contabile (`core/d406.py`), confirmată ca validă pe validatorul oficial ANAF. Aplicația **nu determină automat** dacă o firmă se încadrează, la un moment dat, în categoria mari/mijlocii/mici contribuabili — această încadrare este comunicată contribuabilului de ANAF, iar decizia de a depune sau nu D406 la un anumit moment rămâne responsabilitatea contabilului, pe baza acestei încadrări oficiale.

[iConta.eu](/)
