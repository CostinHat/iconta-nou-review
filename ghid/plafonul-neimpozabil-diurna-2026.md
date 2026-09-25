---
title: "Care este plafonul neimpozabil pentru diurnă în 2026?"
description: "Valoarea diurnei bugetare aplicabile în 2026 și cum se calculează, pornind de la ea, plafonul neimpozabil al indemnizației de delegare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este plafonul neimpozabil pentru diurnă în 2026?

Plafonul de diurnă neimpozabilă nu e o sumă fixă în lege, ci rezultatul unei formule care pornește de la nivelul indemnizației bugetare. Pentru 2026, acel nivel de referință este 23 de lei pe zi, valabil pentru delegările interne de la 1 aprilie 2023 încoace.

## Temeiul legal

::: ghid-temei
„ART. 1 Începând cu data de 1 aprilie 2023: a) cuantumul indemnizației de delegare prevăzute la art. 1 alin. (1) și alin. (2) lit. a) din anexa la Hotărârea Guvernului nr. 714/2018 [...] se majorează la 23 lei; b) cuantumul alocației de cazare prevăzute la art. 1 alin. (2) lit. b) din anexa la Hotărârea Guvernului nr. 714/2018 se majorează la 265 lei; c) cuantumul indemnizației de detașare prevăzute la art. 4 alin. (1) din anexa la Hotărârea Guvernului nr. 714/2018 se majorează la 23 lei."
— Ordinul MF nr. 1235/2023, art. 1 (sursă: anaf_surse/omf_1235_2023.txt)
:::

Ce înseamnă concret aceste 23 de lei pentru plafonul neimpozabil:

- 23 lei/zi este **nivelul legal al indemnizației** pentru personalul bugetar, folosit ca bază de calcul — nu este el însuși „plafonul neimpozabil" al unui salariat din mediul privat.
- Plafonul neimpozabil real, conform art. 76 alin. (2) lit. k) din Codul fiscal, este **2,5 ori** acest nivel — deci 57,5 lei/zi pentru delegări interne, plafonat suplimentar la 3 salarii de bază raportate la zilele lucrătoare din lună (vezi ghidurile despre formula 2,5× și formula celor 3 salarii).
- Pentru perioada 2018 – 31 martie 2023, nivelul de referință era de 20 de lei/zi — o valoare confirmată doar printr-o notă de cercetare internă asupra HG 714/2018, nu printr-un text integral verificat al hotărârii; textul integral al HG 714/2018 nu s-a putut identifica pentru verificare verbatim.
- Pentru delegările **externe**, nivelul de referință nu e 23 de lei, ci un nomenclator pe țări stabilit prin HG 518/1995 (de exemplu, aproximativ 35 EUR/zi pentru majoritatea statelor UE) — un act separat, distinct de cel pentru delegările interne.

## Ce se greșește în practică

- Se confundă „diurna bugetară" (23 lei) cu „plafonul neimpozabil" — plafonul e de 2,5 ori mai mare, nu egal cu nivelul bugetar.
- Se aplică valoarea de 23 lei și pentru deplasări externe, ignorând că acestea au un nomenclator separat, pe țară și valută.
- Se folosește valoarea curentă (23 lei) și pentru decontarea unor deplasări vechi, dinainte de 1 aprilie 2023, când nivelul legal era de 20 de lei.

## Ce face iConta.eu

Motorul de calcul din `core/deconturi.py` cunoaște ambele valori istorice ale diurnei bugetare interne (20 lei până la 31.03.2023, 23 lei după) și e construit să aleagă automat varianta corectă în funcție de data deplasării. Există însă o discrepanță confirmată direct în cod: la apelul efectiv din aplicație (`core/uc_tenants.py`, funcția care procesează decontul), data deplasării introdusă de utilizator **nu este transmisă** motorului de calcul — acesta cade, implicit, pe data curentă a serverului. În consecință, un decont introdus azi pentru o deplasare veche (dinainte de aprilie 2023) ar putea folosi eronat valoarea de 23 lei în loc de 20 lei.

În plus, acest calcul de plafon (`fel="plafon"`) **nu este accesibil din interfața iConta** — ecranul „Decont deplasare / diurnă" nu are opțiunea de a cere un calcul de plafon, doar de a înregistra un avans sau un decont. Un contabil care vrea să afle plafonul aplicabil pentru 2026 trebuie, astăzi, să-l calculeze manual (57,5 lei/zi, cu plafonarea suplimentară la 3 salarii/zile lucrătoare), nu să-l obțină direct din aplicație.

[iConta.eu](/)
