---
title: "Cum se declară vânzarea unui mijloc fix în D300?"
description: D300 nu are un rând separat pentru vânzarea unui mijloc fix — se declară ca orice altă livrare taxabilă, pe rândul automat corespunzător cotei de TVA facturate (R9 la 21%, R10 la 11%, R11 la 9%).
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară vânzarea unui mijloc fix în D300?

Din perspectiva decontului de TVA, vânzarea unui mijloc fix nu are un tratament special — e o livrare de bunuri ca oricare alta, care intră în decont prin cota de TVA facturată, nu printr-un rând dedicat „mijloace fixe".

## Temeiul legal

::: ghid-temei
**Art. 291 Cod fiscal (Legea 227/2015), modificat de Legea 141/2025 art. II pct. 42:** *„(1) Cota standard se aplică asupra bazei de impozitare pentru operaţiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%. (2) Cota redusă de 11% se aplică..."*

**Art. 323 alin. (1) Cod fiscal:** *„... trebuie să depună ... un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă."*
:::

## Cum intră în decont

Structura confirmată în cod (`core/d300.py`, liniile 46-47) mapează fiecare cotă de TVA pe un rând specific de livrare: **21% → R9, 11% → R10, 9% → R11**. Vânzarea unui mijloc fix se declară exact ca orice altă vânzare, pe rândul corespunzător cotei aplicate facturii de vânzare — nu există un rând sau o secțiune separată, în structura verificată, dedicată exclusiv mijloacelor fixe.

Notă din sursele verificate: doar cotele 21%, 11% și 9% au rând automat în această structură — orice altă cotă aplicată (de exemplu una tranzitorie sau specială) „dispare" din decontul automat dacă nu e tratată manual, cu avertisment generat de aplicație.

Un aspect care nu face parte din sursele verificate pentru acest ghid: dacă vânzarea unui mijloc fix declanșează o obligație de **ajustare** a TVA deja dedusă la achiziția lui (regim distinct de simpla colectare a TVA la vânzare, reglementat separat în Codul fiscal). Acest calcul de ajustare nu a fost identificat ca funcționalitate acoperită de dosarul verificat pentru D300 — dacă situația se aplică, e un calcul separat, făcut în afara mecanismului descris aici.

## Ce se greșește în practică

- **Se caută un rând special „mijloc fix" în D300** — nu există; vânzarea intră pe rândul cotei de TVA aplicate (R9/R10/R11), ca orice altă livrare.
- **Se omite verificarea unei eventuale obligații de ajustare a TVA deduse la achiziția mijlocului fix** — acest calcul e distinct de simpla colectare a TVA la vânzare și nu e acoperit de mecanismul de bază al decontului.
- **Se aplică o cotă „specială" pentru mijloace fixe** — nu există un regim de cotă distinct pentru vânzarea de mijloace fixe; se aplică cota standard sau redusă, ca la orice altă livrare de bunuri.

## Ce face iConta.eu

Decontul de TVA v12 (`core/d300.py`) rutează automat orice livrare — inclusiv vânzarea unui mijloc fix — pe rândul corespunzător cotei facturate (R9 la 21%, R10 la 11%, R11 la 9%), cu avertisment explicit dacă apare o cotă neobișnuită, netratată automat. Aplicația nu calculează separat o eventuală ajustare a TVA deduse la achiziția mijlocului fix vândut — acel calcul, dacă e aplicabil, rămâne în afara acestui mecanism.

[iConta.eu](/)
