---
title: "Cum se înregistrează contabil TVA plătită prin D301?"
description: "D301 e decontul special de TVA pentru achiziții intracomunitare/operațiuni cu taxare inversă ale persoanelor neînregistrate normal în scopuri de TVA — cum se reflectă contabil taxa astfel plătită."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează contabil TVA plătită prin D301?

D301 e declarația specifică persoanelor care nu sunt înregistrate normal în scopuri de TVA (conform art. 316), dar care, printr-o achiziție intracomunitară sau o operațiune cu taxare inversă, ajung totuși să datoreze TVA la bugetul de stat. Contabil, taxa plătită astfel nu se comportă ca un TVA deductibil obișnuit.

## Temeiul legal

::: ghid-temei
„decontul special de taxă reprezintă decontul care se întocmește și se depune conform art. 324."
— Legea nr. 227/2015 privind Codul fiscal, definiție conexă art. 324 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Decontul special de taxă se depune la organele fiscale competente de către persoanele care nu sunt înregistrate și care nu trebuie să se înregistreze conform art. 316, astfel: a) pentru achiziții intracomunitare de bunuri taxabile, altele decât cele prevăzute la lit. b) și c), de către persoanele impozabile înregistrate conform art. 317; [...] d) pentru operațiunile și de către persoanele obligate la plata taxei, conform art. 307 alin. (2)-(4) și (6); [...]"
— Legea nr. 227/2015 (Codul fiscal), art. 324 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta pentru contabilizare:

- D301 se depune de **persoane neînregistrate normal în scopuri de TVA** (fără cod de TVA prin art. 316) care fac totuși achiziții intracomunitare taxabile, achiziții de mijloace de transport noi, achiziții de produse accizabile sau operațiuni pentru care sunt obligate la plata taxei prin taxare inversă (art. 331).
- Pentru aceste persoane, TVA plătită prin D301 **nu poate fi dedusă** printr-un decont normal de TVA (formularul 300), pentru că nu sunt înregistrate în scopuri de TVA — taxa plătită intră, de regulă, în costul bunului/serviciului achiziționat, nu într-un cont de TVA deductibil recuperabil.
- Contabil, operațiunea presupune calcularea TVA pe baza cursului valutar și a bazei impozabile declarate, plata efectivă a sumei la buget, și înregistrarea ei ca parte a costului de achiziție al bunului (majorând valoarea de intrare în gestiune), nu ca o creanță de recuperat de la stat.

## Ce se greșește în practică

- Se tratează TVA din D301 ca TVA deductibil obișnuit, încercând să fie scăzut dintr-un decont 300 — deși persoana care depune D301 nu e, prin definiție, înregistrată normal în scopuri de TVA și nu are drept de deducere pe acest circuit.
- Se omite includerea TVA plătit prin D301 în costul de achiziție al bunului, ceea ce subevaluează stocul/imobilizarea și, ulterior, cheltuiala cu amortizarea sau costul vânzărilor.
- Se confundă D301 cu decontul normal de TVA (300) ca formă și scop, deși cele două se adresează unor categorii de contribuabili complet diferite.

## Ce face iConta.eu

iConta.eu generează declarația D301 pe baza operațiunilor introduse (achiziții intracomunitare, valute, cursuri, tipuri de operațiune conform nomenclatorului oficial), cu calculul bazei și al taxei aferente conform validatorului ANAF instalat. Includerea automată a sumei plătite prin D301 în costul de achiziție al bunului, în contabilitatea generală, nu este un pas automatizat al modulului D301 — legătura dintre suma declarată și înregistrarea contabilă a costului rămâne o operațiune separată, realizată de contabil.

[iConta.eu](/)
