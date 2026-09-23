---
title: Cum ține gestiunea o firmă micro cu amănuntul?
description: Regimul fiscal (micro sau profit) nu schimbă regulile de gestiune a mărfurilor — metoda global-valorică se aplică identic, indiferent de impozitul pe care îl plătește firma; singura diferență e la calculul impozitului, nu la organizarea stocurilor.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum ține gestiunea o firmă micro cu amănuntul?

O microîntreprindere cu magazin de amănuntul ține gestiunea mărfurilor exact ca orice altă firmă cu amănuntul — regulile din OMFP 1802/2014 pentru evidența stocurilor nu depind de regimul de impozitare al firmei. Impozitul micro (pe venit) și evaluarea stocurilor sunt două lucruri complet independente.

## Temeiul legal

::: ghid-temei
„... pentru determinarea costului pot fi folosite, de asemenea, metoda costului standard, în activitatea de producție sau metoda prețului cu amănuntul, în comerțul cu amănuntul.”

— *OMFP 1802/2014, pct. 286 alin. (1).*

„Inventarul intermitent nu se utilizează în comerțul cu amănuntul în situația în care se aplică metoda global-valorică.”

— *OMFP 1802/2014, pct. 291 alin. (5).*
:::

## Ce nu se schimbă la o firmă micro

Obligațiile de evidență a stocurilor (recepție, gestiune, descărcare lunară, coeficient de adaos) vin din legea contabilității și din OMFP 1802/2014 — norme aplicabile tuturor firmelor care țin contabilitate în partidă dublă, indiferent dacă plătesc impozit pe veniturile microîntreprinderilor sau impozit pe profit. O microîntreprindere cu magazin de amănuntul:

- ține gestiunea la preț cu amănuntul (metoda global-valorică) exact ca o firmă plătitoare de impozit pe profit, cu aceleași conturi (371, 378, 4428) și aceeași formulă de coeficient de adaos;
- descarcă gestiunea lunar, cu aceleași reguli de calcul cumulat de la 1 ianuarie;
- nu poate folosi inventarul intermitent dacă aplică metoda global-valorică — interdicția din pct. 291 alin. (5) e legată de metoda de gestiune aleasă, nu de regimul fiscal al firmei.

## Ce se greșește în practică

- Se presupune că o firmă micro are reguli „simplificate” de gestiune a mărfii — simplificarea specifică micro-urilor privește calculul impozitului pe venit (cotă redusă, bază de impozitare pe venituri), nu evidența stocurilor.
- Se amână descărcarea de gestiune sau se ține evidența doar global, fără conturile 378/4428, pe motiv că firma e „doar micro” — obligația de a organiza corect gestiunea mărfurilor (partidă dublă, conturi de mărfuri) nu depinde de impozitul aplicat.
- Se confundă facilitatea fiscală (abrogată din 2024) de deducere a sponsorizării din impozitul micro cu vreo facilitate similară pentru gestiunea stocurilor — nu există o astfel de facilitate de simplificare a gestiunii la micro.

## Ce face iConta.eu

Motorul de gestiune global-valorică (`core/stocuri.py` + `core/stocuri_api.py`) nu are niciun parametru sau ramură de cod legată de regimul de impozitare al firmei (micro vs. profit) — funcțiile `nir_gv`, `coeficient_k` și `descarcare_gv` calculează identic, indiferent dacă tenantul e configurat ca plătitor de impozit micro sau de impozit pe profit. Impozitul propriu-zis (D101 pentru profit, sau declarația specifică micro) se calculează separat, din alte module, fără nicio legătură cu motorul de stocuri.

[iConta.eu](/)
