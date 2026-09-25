---
title: "SAF-T pentru firmele din HoReCa: particularități"
description: "Cine e obligat să depună D406/SAF-T și de ce obligația nu depinde de codul CAEN — ce înseamnă asta pentru un restaurant sau bar."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# SAF-T pentru firmele din HoReCa: particularități

Fișierul standard de control fiscal (SAF-T, declarația D406) nu are un regim separat pentru restaurante și baruri. Obligația de depunere se stabilește după **categoria de contribuabil** (mare, mijlociu, mic), nu după codul CAEN al activității — deci, din perspectivă pur declarativă, o firmă din HoReCa depune D406 exact ca orice altă firmă din aceeași categorie de mărime.

## Temeiul legal

::: ghid-temei
„Obligaţia de transmitere a fişierului standard de control fiscal prin intermediul Declaraţiei informative D406 devine efectivă pentru fiecare categorie de contribuabili, astfel: [...] pentru contribuabilii încadraţi în categoria contribuabili mijlocii la data de 31 decembrie 2021, obligaţia de depunere a Declaraţiei informative D406 începe de la data de 1 ianuarie 2023 [...]; pentru contribuabilii încadraţi în categoria de contribuabili mici la data de 31 decembrie 2021, obligaţia de depunere a Declaraţiei informative D406 începe de la data de 1 ianuarie 2025 [...]; pentru contribuabilii nou-înregistraţi/încadraţi după data de referinţă pentru fiecare categorie în parte, obligaţia de depunere a Declaraţiei informative D406 începe de la data efectivă a înregistrării [...]"
— OPANAF 1783/2021, Anexa 5 pct. 1 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce rezultă pentru o firmă din HoReCa (CAEN 5610 „Restaurante", 5630 „Baruri"):

- **Termenul de intrare în obligația SAF-T se stabilește după mărimea contribuabilului** (mare/mijlociu/mic la data de referință), nu după activitatea desfășurată — un restaurant încadrat drept contribuabil mic intră în obligație la aceeași dată de referință ca orice altă firmă mică, indiferent de domeniu.
- Nu există, în actul normativ, o secțiune sau un termen dedicat exclusiv HoReCa — periodicitatea (lunară/trimestrială/anuală) și structura fișierului urmează regulile generale (perioada TVA a firmei pentru declarațiile periodice, respectiv anual pentru secțiunile Assets/Fixed Assets).
- Particularitatea reală a HoReCa nu vine din SAF-T, ci din alte obligații conexe (bacșișul evidențiat distinct pe bonul fiscal, conform Legii 376/2022) — care, o dată contabilizate, intră în evidența contabilă generală și, de acolo, în orice raportare care citește Cartea Mare, inclusiv D406.

## Ce se greșește în practică

- Se caută în legislație un regim SAF-T „pentru HoReCa" separat — nu există; obligația și termenele sunt identice cu ale oricărei alte firme din aceeași categorie de mărime.
- Se confundă particularitățile fiscale reale ale HoReCa (bacșișul, taxarea specifică) cu o presupusă particularitate de raportare SAF-T — bacșișul e o operațiune contabilă ca oricare alta, fără tratament distinct în structura D406.
- Se amână depunerea D406 crezând că un restaurant/bar mic e „exceptat" prin natura activității — excepțiile de la SAF-T țin de categoria de contribuabil și de alte criterii generale, nu de codul CAEN.

## Ce face iConta.eu

Generatorul D406/SAF-T (`core/d406.py`) e generic — nu conține nicio ramură specifică pentru CAEN-urile HoReCa și nu tratează diferit o firmă de restaurant sau bar față de oricare alta. Secțiunea GeneralLedgerEntries se construiește din **toate** notele contabile validate ale perioadei, indiferent de operațiune: dacă firma folosește și modulul de Bacșiș HoReCa (notele 461=462 la încasare, 462=446/5121/5311 la distribuire către salariați), acele note intră în raportare exact ca oricare altă notă validată, fără tratament special. La fel funcționează și secțiunile pentru mijloace fixe (D406 Active) și stocuri la cerere (D406 Stocuri) — generice, alimentate din registrele proprii ale firmei, nu adaptate pe domeniul de activitate.

[iConta.eu](/)
