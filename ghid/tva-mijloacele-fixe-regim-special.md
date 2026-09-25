---
title: "TVA la mijloacele fixe cu regim special de deducere"
description: "Ce înseamnă de fapt regula de ajustare a taxei deductibile pentru bunurile de capital (mijloace fixe) și de ce nu e un regim opțional, ci o obligație de recalculare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# TVA la mijloacele fixe cu regim special de deducere

Expresia „regim special de deducere" folosită informal pentru mijloacele fixe se referă, de fapt, la **ajustarea taxei deductibile pentru bunurile de capital** — un mecanism obligatoriu de recalculare a TVA dedusă inițial, atunci când destinația sau folosința bunului se schimbă pe parcursul unei perioade de monitorizare fiscală. Nu e un regim la alegere, ci o corecție impusă de lege ori de câte ori apar situațiile prevăzute expres.

## Temeiul legal

::: ghid-temei
„(1) În sensul prezentului articol: a) bunurile de capital reprezintă toate activele corporale fixe, definite la art. 266 alin. (1) pct. 3 [...]
(2) Taxa deductibilă aferentă bunurilor de capital [...] se ajustează, în situațiile prevăzute la alin. (4) lit. a)-d): a) pe o perioadă de 5 ani, pentru bunurile de capital achiziționate sau fabricate, altele decât cele prevăzute la lit. b); b) pe o perioadă de 20 de ani, pentru construcția sau achiziția unui bun imobil, precum și pentru transformarea sau modernizarea unui bun imobil, dacă valoarea fiecărei transformări sau modernizări este de cel puțin 20% din valoarea totală a bunului imobil [...] după transformare sau modernizare."
— Legea nr. 227/2015 (Codul fiscal), art. 305 alin. (1) lit. a) și alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Ajustarea se declanșează în patru situații, prevăzute la alin. (4): schimbarea destinației de utilizare a bunului (ex. trece de la activitate economică la scop personal, sau de la operațiuni cu drept de deducere la operațiuni fără drept de deducere), modificarea elementelor folosite la calculul taxei deduse (ex. schimbarea pro-ratei), o operațiune ulterioară care redă dreptul de deducere unui bun limitat inițial, sau încetarea existenței bunului (casare, pierdere, furt, livrare).
- Ajustarea se face **fracționat**: o cincime (1/5) din taxa dedusă inițial pentru fiecare an din perioada de 5 ani, respectiv o douăzecime (1/20) pentru fiecare an din perioada de 20 de ani la imobile — nu integral, dintr-o dată, decât în cazurile expres prevăzute (ex. casare, art. 305 alin. (5) lit. d)).
- Perioada de ajustare pornește de la 1 ianuarie a anului achiziției/fabricării (bunuri mobile) sau al recepției/primei utilizări (imobile, transformări) — art. 305 alin. (3).

## Ce se greșește în practică

- Se numește informal „regim special de deducere", dar de fapt e o **obligație de ajustare** — nu se poate opta să nu se aplice, dacă intervine una din situațiile de la alin. (4).
- Se confundă cu regularizarea normală de TVA (art. 304) sau cu ajustarea pro-rata anuală (art. 300) — sunt mecanisme diferite, cu reguli și baze de calcul proprii, deși toate apar pe aceleași rânduri din decontul de TVA (D300).
- Se aplică perioada greșită: 5 ani pentru un bun imobil (când legea cere 20 de ani) sau invers, 20 de ani pentru un echipament tehnologic mobil.
- Se omite ajustarea la casarea, pierderea, distrugerea sau furtul unui mijloc fix pentru care s-a dedus inițial TVA — situație care declanșează ajustare pentru toată taxa aferentă perioadei rămase, dintr-o dată, nu eșalonat.

## Ce face iConta.eu

În motorul de calcul al decontului de TVA (D300) din iConta.eu, rândurile de ajustare/regularizare aferente bunurilor de capital (art. 305) se **declară manual** de către contabil și sunt preluate ca atare în totalurile declarației — aplicația nu calculează automat fracția de 1/5 sau 1/20 din taxa dedusă inițial, nu ține un calendar al perioadei de monitorizare de 5 sau 20 de ani și nu detectează singură când a intervenit un eveniment care declanșează ajustarea. Determinarea sumei de ajustat, conform art. 305, rămâne responsabilitatea profesională a contabilului; iConta.eu se ocupă doar de a duce corect suma declarată manual în rândul corespunzător al D300.

[iConta.eu](/)
