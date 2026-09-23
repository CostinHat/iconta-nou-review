---
title: "Greșeli la D394: operațiuni raportate incorect"
description: Cele mai frecvente greșeli — declararea achizițiilor intracomunitare (care nu intră în D394), omiterea livrărilor IC/exporturilor scutite și bifa de operațiuni cu persoane afiliate necompletată manual.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeli la D394: operațiuni raportate incorect

D394 e declarația operațiunilor cu locul în România — nu orice operațiune a firmei. Cele mai des întâlnite greșeli vin din confuzia cu alte declarații sau din omiterea unor categorii care par, la prima vedere, excluse.

## Temeiul legal

::: ghid-temei
"Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390." — OPANAF nr. 2194/2025, Anexa 2, pct. 1 lit. b)
:::

::: ghid-temei
"Declaraţia se depune la organul fiscal competent până în data de 30 inclusiv a lunii următoare încheierii perioadei de raportare..." — OPANAF nr. 2194/2025, Anexa 2, pct. 2
:::

Greșeli frecvente, confirmate din normă și din comportamentul aplicației:

- **Se declară în D394 achiziții intracomunitare** — acestea sunt excluse explicit, fiindcă se raportează în D390, nu în D394.
- **Se omit livrările intracomunitare și exporturile** — deși nu sunt achiziții, ci livrări, acestea *rămân* în D394 (tip L, reclasificat LS la cotă 0), spre deosebire de achizițiile IC; regula de excludere vizează doar direcția "primită" de la parteneri UE/non-UE.
- **Se omite o livrare scutită cu cotă 0 către un partener cu CUI** — o astfel de livrare trebuie inclusă (tip LS), nu ignorată doar pentru că nu are TVA.
- **Se lasă nebifată/necorectată bifa "operațiuni cu persoane afiliate"** — acest câmp nu se completează automat din tranzacții, trebuie bifat manual, dacă e cazul.
- **Se presupune un plafon de cifră de afaceri** pentru obligația D394 — nu există; obligația e legată exclusiv de înregistrarea în scopuri de TVA.

## Ce se greșește în practică

- Se amestecă regulile D390 și D394 pentru operațiuni intracomunitare, considerând că orice operațiune cu partener UE se declară identic în ambele.
- Se ignoră bifa persoanelor afiliate, presupunând că aplicația o completează automat din facturi.
- Se aplică termenul vechi de 25 (valabil până la 1 august 2025), în loc de termenul actual de 30 (28/29 februarie pentru ianuarie).

## Ce face iConta.eu

Achizițiile intracomunitare sunt excluse automat din D394, cu comentariu explicit în cod care citează motivul: se declară în D390, nu în D394. Livrările scutite cu cotă 0 sunt incluse automat ca tip LS, indiferent de tipul partenerului, după o reparație aplicativă concretă pentru cazul unei livrări scutite către un partener cu CUI care era anterior omisă tacit. Bifa de operațiuni cu persoane afiliate rămâne declarată manual de contabil — aplicația nu o derivă automat din tranzacții, exact pentru a nu produce o "deducere" nesigură.

[iConta.eu](/)
