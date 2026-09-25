---
title: "Cum se declara tranzacțiile cu părți afiliate"
description: "Obligația de a întocmi dosarul prețurilor de transfer pentru tranzacțiile cu persoane afiliate, potrivit Codului de procedură fiscală, și declararea lor prin bifa dedicată din D394."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declara tranzacțiile cu părți afiliate

Declararea tranzacțiilor cu părți afiliate are două fațete legale distincte: obligația de fond, de a documenta respectarea principiului valorii de piață printr-un dosar al prețurilor de transfer, și obligația formală, de a semnala existența acestor tranzacții în declarațiile informative periodice.

## Temeiul legal

::: ghid-temei
„(2) în vederea documentării respectării principiului valorii de piață contribuabilul/plătitorul care desfășoară tranzacții cu persoane afiliate are obligația să întocmească dosarul prețurilor de transfer. La solicitarea organului fiscal central competent contribuabilul/plătitorul are obligația de a prezenta dosarul prețurilor de transfer. Cuantumul tranzacțiilor pentru care contribuabilul/plătitorul are obligația întocmirii dosarului prețurilor de transfer, termenele pentru întocmirea acestuia, conținutul dosarului prețurilor de transfer, precum și condițiile în care se solicită acesta se aprobă prin ordin al președintelui A.N.A.F."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 108 alin. (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce rezultă din text pentru declararea tranzacțiilor cu părți afiliate:

- Obligația de bază este **documentarea**, prin dosarul prețurilor de transfer, a faptului că tranzacțiile cu persoane afiliate respectă principiul valorii de piață — nu doar simpla lor evidențiere contabilă.
- Pragurile valorice de la care dosarul devine obligatoriu și termenele de întocmire nu sunt fixate în acest articol, ci printr-un ordin separat al președintelui A.N.A.F., neinclus integral în sursele verificate aici.
- Separat de dosarul prețurilor de transfer, existența operațiunilor cu persoane afiliate în perioada de raportare se semnalează și printr-o bifă dedicată în declarația D394 (indicatorul „prsAfiliat").

## Ce se greșește în practică

- Se presupune că bifarea „da" la tranzacții cu persoane afiliate în D394 acoperă și obligația de întocmire a dosarului prețurilor de transfer — sunt obligații distincte, una declarativă, cealaltă de documentare de fond.
- Se ignoră relația de afiliere atunci când aceasta rezultă indirect (deținere de peste 25% din capital, drept de numire a administratorului), nu doar din asociere directă evidentă.
- Se întocmește dosarul prețurilor de transfer abia la solicitarea organului fiscal, deși obligația de întocmire există independent de o eventuală cerere — cererea declanșează doar termenul de prezentare.

## Ce face iConta.eu

Verificat în cod: `core/d394.py` populează indicatorul „prsAfiliat" din formularul D394 pe baza unui flag explicit din profilul firmei (`are_operatiuni_afiliate`), fără să-l deducă automat din relațiile de acționariat sau din tranzacțiile efective cu partenerii; aplicația nu are, la acest moment, un model de „persoană afiliată" (nicio coloană dedicată în profilul firmei, clienți sau furnizori) și nu generează dosarul prețurilor de transfer — încadrarea unei tranzacții ca fiind cu o parte afiliată și documentarea aferentă rămân, integral, responsabilitatea contabilului.

[iConta.eu](/)
