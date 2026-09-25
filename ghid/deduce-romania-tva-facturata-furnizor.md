---
title: "Pot deduce în România TVA facturată de un furnizor din alt stat UE?"
description: "TVA facturat greșit de un furnizor dintr-un alt stat membru, pe o operațiune al cărei loc e în România, nu se poate deduce prin decontul românesc — furnizorul trebuie să corecteze factura."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Pot deduce în România TVA facturată de un furnizor din alt stat UE?

O firmă din România primește o factură de la un furnizor dintr-un alt stat membru, pe care apare TVA din statul acelui furnizor, pentru un serviciu al cărui loc de prestare e, de fapt, în România. Răspunsul scurt e nu — acel TVA nu se poate deduce prin decontul românesc, indiferent cât de corectă pare factura la prima vedere.

## Temeiul legal

::: ghid-temei
„Pentru exercitarea dreptului de deducere a taxei, persoana impozabilă trebuie să îndeplinească următoarele condiții: a) pentru taxa datorată sau achitată, aferentă bunurilor care i-au fost ori urmează să îi fie livrate ori serviciilor care i-au fost ori urmează să îi fie prestate în beneficiul său de către o persoană impozabilă, să dețină o factură emisă în conformitate cu prevederile art. 319."
— Codul fiscal (Legea 227/2015), art. 299 alin. (1) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Dreptul de deducere din decontul românesc de TVA privește doar taxa datorată potrivit legii române — nu orice sumă etichetată „TVA" pe o factură:

- Dacă locul prestării serviciului e în România (art. 278 alin. (2), regula B2B), furnizorul din alt stat membru **nu ar fi trebuit să factureze cu TVA din statul lui** — obligația de plată trece la beneficiar, prin taxare inversă (art. 307 alin. (2)).
- TVA-ul facturat greșit de furnizor **nu e TVA românesc** și nu se poate trece la rubrica de taxă deductibilă din decontul D300 — art. 297 și 299 vizează taxa datorată conform titlului VII din Codul fiscal românesc, nu taxa unui alt stat.
- Soluția corectă e să se ceară furnizorului o **factură de corecție**, fără TVA, cu mențiunea de taxare inversă, iar beneficiarul să înregistreze operațiunea prin mecanismul de taxare inversă (4426 = 4427).

## Ce se greșește în practică

- Se deduce TVA-ul altui stat ca și cum ar fi TVA românesc, prin simpla introducere a facturii în decont — la un control, suma nu poate fi justificată drept taxă deductibilă potrivit Codului fiscal românesc.
- Se plătește factura cu TVA inclus, fără să se solicite furnizorului corectarea ei, ceea ce lasă firma cu o taxă plătită degeaba unui furnizor care, la rândul lui, ar fi trebuit să nu o factureze.
- Se confundă acest caz cu situația în care TVA-ul e corect facturat de statul membru respectiv (pentru operațiuni al căror loc chiar e acolo) — atunci recuperarea se face prin procedura de rambursare transfrontalieră (D318), nu prin decontul românesc.

## Ce face iConta.eu

iConta.eu **nu blochează și nu semnalează automat** o factură de achiziție intracomunitară pe care apare TVA din alt stat membru pentru o operațiune al cărei loc corect e în România — verificarea revine contabilului la introducerea facturii. Odată identificată corect operațiunea ca taxare inversă, aplicația generează nota contabilă corespunzătoare și preia automat suma în D300 și D390.

[iConta.eu](/)
