---
title: "Monografia contabilă la vânzarea unui mijloc fix 2026"
description: "Conturile prin care se înregistrează vânzarea unui mijloc fix — venitul din vânzare și descărcarea din gestiune — potrivit funcțiunii conturilor din OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Monografia contabilă la vânzarea unui mijloc fix 2026

Vânzarea unui mijloc fix presupune două operațiuni contabile distincte, care se înregistrează simultan: recunoașterea venitului din vânzare și scoaterea din evidență a activului, cu partea deja amortizată separată de valoarea rămasă neamortizată.

## Temeiul legal

::: ghid-temei
„În creditul contului 213 «Instalații tehnice și mijloace de transport» se înregistrează: – valoarea neamortizată a instalațiilor tehnice și mijloacelor de transport scoase din evidență (658); – amortizarea instalațiilor tehnice și a mijloacelor de transport scoase din evidență (281); [...]"
— OMFP 1802/2014 (Reglementări contabile), Funcțiunea conturilor, contul 213 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Din funcțiunea contului rezultă mecanismul, aplicabil similar oricărui cont de mijloc fix (211, 212, 213, 214 etc.):

- **Descărcarea din gestiune** a mijlocului fix vândut se face pe două componente separate: **amortizarea deja înregistrată** (contul 281 „Amortizări privind imobilizările corporale") și **valoarea neamortizată rămasă** (contul 658/6583 „Cheltuieli privind activele cedate și alte operațiuni de capital"), ambele în creditul contului de imobilizare (211/212/213/214, după caz).
- **Recunoașterea venitului din vânzare** se face separat, prin contul **7583 „Venituri din vânzarea activelor și alte operațiuni de capital"**, cu contrapartidă în contul de clienți/debitori (461), inclusiv TVA colectată (4427), acolo unde operațiunea e taxabilă.
- Practic, monografia standard pentru vânzarea unui mijloc fix cuprinde deci: **461 = 7583 + 4427** (facturarea vânzării, cu TVA) și, în paralel, **2813 (sau contul de amortizare corespunzător) + 6583 = 21x** (descărcarea din gestiune, cu amortizarea acumulată separată de valoarea rămasă neamortizată).
- Rezultatul din vânzare (câștig sau pierdere) nu e o operațiune contabilă separată — el rezultă automat din diferența dintre venitul recunoscut la 7583 și cheltuiala recunoscută la 6583, fără o notă contabilă suplimentară.

## Ce se greșește în practică

- Se descarcă mijlocul fix printr-o singură notă, cu întreaga valoare de intrare, fără să se separe amortizarea deja înregistrată (281) de valoarea neamortizată rămasă (6583) — cele două componente au regimuri și implicații fiscale diferite.
- Se omite recunoașterea TVA colectată la vânzare, tratând tranzacția doar ca o ieșire de activ, fără factură și fără componenta de TVA aferentă.
- Se confundă venitul din vânzare (7583) cu rezultatul net al operațiunii — rezultatul (câștig/pierdere) nu se înregistrează separat, ci reiese din compararea automată a veniturilor și cheltuielilor aferente celor două note.

## Ce face iConta.eu

iConta.eu generează automat această monografie (461 = 7583 + 4427, cu descărcarea 6583 + amortizare = cont imobilizare) în modulul de lichidare, la valorificarea activelor firmei aflate în dizolvare. Pentru vânzarea unui mijloc fix în cursul normal al activității (în afara lichidării), generarea automată a acestei monografii nu este disponibilă ca funcție separată — notele contabile corespunzătoare rămân introduse de contabil pe baza documentelor operațiunii.

[iConta.eu](/)
