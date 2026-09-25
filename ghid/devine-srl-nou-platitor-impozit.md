---
title: "Când devine un SRL nou plătitor de impozit pe profit?"
description: "Condițiile cumulative din Codul fiscal pentru statutul de microîntreprindere în 2026 și momentul exact în care un SRL nou-înființat trece la impozit pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când devine un SRL nou plătitor de impozit pe profit?

Un SRL nou-înființat intră, de regulă, direct în regimul de microîntreprindere (1% pe venituri), nu în impozit pe profit. Trecerea la profit se produce fie pentru că nu îndeplinește de la început condițiile de microîntreprindere, fie pentru că le pierde ulterior — cel mai frecvent prin depășirea plafonului de venituri sau prin neangajarea niciunui salariat în termenul legal.

## Temeiul legal

::: ghid-temei
„În sensul prezentului titlu, o microîntreprindere este o persoană juridică română care îndeplinește cumulativ următoarele condiții, la data de 31 decembrie a anului fiscal precedent: [...] c) a realizat venituri care nu au depășit echivalentul în lei a 100.000 euro. [...] d) capitalul social al acesteia este deținut de persoane, altele decât statul și unitățile administrativ-teritoriale; e) nu se află în dizolvare, urmată de lichidare [...]; g) are cel puțin un salariat, cu excepția situației prevăzute la art. 48 alin. (3); h) are asociați/acționari care dețin, în mod direct sau indirect, peste 25% din valoarea/numărul titlurilor de participare [...] și este singura persoană juridică stabilită [...] să aplice prevederile prezentului titlu; i) a depus în termen situațiile financiare anuale, dacă are această obligație potrivit legii."
— Legea 227/2015, art. 47 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta pentru un SRL nou:

- Plafonul de venituri e **100.000 euro** (modificat prin OUG 8/2026, aplicabil pentru verificarea condițiilor începând cu anul fiscal 2026) — coborât față de plafoanele mai mari din anii anteriori.
- Condiția salariatului (lit. g) e obligatorie din primul an — dacă firma nu are niciun salariat, iese din micro, cu excepțiile de la art. 48 alin. (3) (de regulă un termen de grație pentru firmele nou-înființate să angajeze).
- Condiția de la lit. h) limitează la o singură firmă din grup dreptul de a aplica micro, atunci când aceiași asociați dețin peste 25% în mai multe SRL-uri — celelalte intră automat la profit.
- Depășirea plafonului de venituri, neangajarea unui salariat sau nedepunerea la timp a situațiilor financiare anuale duc, fiecare, la trecerea obligatorie la impozit pe profit, de regulă începând cu trimestrul în care a avut loc depășirea (nu retroactiv pe tot anul).

## Ce se greșește în practică

- Se verifică plafonul de venituri raportat la anul curent, în loc de anul fiscal precedent încheiat, așa cum cere art. 47 alin. (1) („la data de 31 decembrie a anului fiscal precedent").
- Se presupune că un SRL nou-înființat e automat micro pe termen nelimitat, fără să se urmărească termenul de grație pentru angajarea unui salariat (art. 48 alin. (3)) sau condiția legăturii cu alte firme ale acelorași asociați (lit. h).
- Se ignoră faptul că plafonul de venituri s-a schimbat pentru 2026 (100.000 euro) față de anii anteriori — o firmă încadrată corect micro în 2025 poate ieși din regim doar prin schimbarea pragului legal, fără nicio modificare a activității ei.

## Ce face iConta.eu

Regimul fiscal (micro sau profit) e un **câmp ales manual** în ecranul de configurare a firmei din iConta.eu — aplicația nu urmărește automat plafonul de 100.000 euro, numărul de salariați sau apartenența la un grup de firme legate, ca să recomande sau să forțeze schimbarea regimului. Câmpul `regim_fiscal` din profilul firmei (`core/d100.py`) determină doar cum se calculează obligația D100 (cod 121 pe venituri, pentru micro, respectiv cod 103 pe profit, pentru regimul de profit) — D100 rămâne declarația lunară/trimestrială pentru ambele regimuri, iar D101 (declarația anuală privind impozitul pe profit, `core/d101.py`) devine relevantă suplimentar doar pentru firmele pe profit. Generatorul nu blochează efectiv generarea unei declarații „nepotrivite" cu regimul setat — verificarea condițiilor de încadrare din art. 47 și coerența dintre regimul real al firmei și declarațiile generate rămân, la acest moment, în sarcina contabilului.

[iConta.eu](/)
