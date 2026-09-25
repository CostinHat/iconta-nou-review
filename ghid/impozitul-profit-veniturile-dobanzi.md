---
title: "Impozitul pe profit la veniturile din dobânzi"
description: "De ce dobânzile încasate de o firmă (cont 766) sunt venituri impozabile integral la calculul impozitului pe profit, potrivit regulii generale din art. 19 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Impozitul pe profit la veniturile din dobânzi

O firmă plătitoare de impozit pe profit care primește dobânzi — de la un depozit bancar, de la un împrumut acordat unei alte entități sau din alte plasamente — nu are, pentru aceste venituri, un regim fiscal separat sau o scutire specială. Dobânda încasată intră, ca orice alt venit, în rezultatul fiscal impozabil.

## Temeiul legal

::: ghid-temei
„Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. [...] Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală."
— Codul fiscal (Legea 227/2015), art. 19 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regula e simplă, dar merită explicată în context:

- rezultatul fiscal pornește de la **toate** veniturile și cheltuielile înregistrate contabil, din care se scad doar veniturile enumerate expres de lege ca fiind neimpozabile;
- veniturile din dobânzi (înregistrate contabil pe contul 766 „Venituri din dobânzi") **nu figurează** printre veniturile neimpozabile prevăzute de Codul fiscal pentru impozitul pe profit — deci rămân integral în baza de calcul, alături de veniturile din exploatare;
- nu există, pentru o societate plătitoare de impozit pe profit, o cotă distinctă sau o reținere la sursă pe dobânzile primite de la o bancă românească — impozitarea se face prin includerea în rezultatul fiscal trimestrial/anual, la cota standard de impozit pe profit;
- situația diferă pentru persoanele fizice (impozitate la sursă, potrivit regulilor din Titlul IV al Codului fiscal, privind venitul din investiții) și pentru anumite categorii speciale (de exemplu obligațiunile emise pe piețe de capital din afara României, cu regim propriu la art. 97^1 CF) — dar acestea nu se aplică unei persoane juridice plătitoare de impozit pe profit pentru dobânzile obișnuite primite.

## Ce se greșește în practică

- Se presupune, din analogie cu impozitarea persoanelor fizice, că dobânda primită de firmă ar fi „deja impozitată la sursă" de bancă și nu mai trebuie inclusă în calculul impozitului pe profit — fals; regimul de reținere la sursă privește dobânzile plătite persoanelor fizice sau anumitor nerezidenți, nu veniturile din dobânzi ale unei persoane juridice române.
- Se omite includerea dobânzii din extrasul de cont bancar în veniturile financiare (cont 766) atunci când suma e mică sau apare direct ca „bonificație" în extras, fără document justificativ explicit.
- Se scade dobânda din baza impozabilă considerând-o, greșit, „venit neimpozabil" prin analogie cu alte venituri financiare scutite — lista veniturilor neimpozabile e limitativă și dobânda obișnuită nu se regăsește pe ea.

## Ce face iConta.eu

iConta.eu include automat veniturile financiare (conturile din clasa 76x, deci și dobânzile de pe contul 766) în baza de calcul recalculată independent la reconcilierea declarațiilor — motorul de reconciliere însumează rulajul creditor al conturilor de venituri 70x, 75x și 76x (minus contul 709) din liniile de contabilitate validate, exact cum cere regula generală a art. 19 alin. (1) pentru rezultatul fiscal. Contabilul rămâne responsabil să înregistreze dobânda din extrasul bancar pe contul corect, pe baza documentului justificativ.

[iConta.eu](/)
