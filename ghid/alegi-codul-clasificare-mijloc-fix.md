---
title: Cum alegi codul de clasificare pentru un mijloc fix?
description: Codul de clasificare al unui mijloc fix determină, deopotrivă, intervalul de durată normală de funcționare din catalogul HG 2139/2004 și metodele de amortizare permise de Codul fiscal - alegerea corectă influențează amândouă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum alegi codul de clasificare pentru un mijloc fix?

Codul de clasificare al unui mijloc fix nu e o simplă formalitate: de el depind, simultan, intervalul legal de durată de amortizare (din catalogul HG 2139/2004) **și** metodele de amortizare pe care legea le permite pentru acel activ (din Codul fiscal). O clasificare greșită poate duce la o durată nepotrivită sau la o metodă de amortizare pe care legea n-o acceptă pentru acea categorie.

## Temeiul legal

::: ghid-temei
Regimul de amortizare pentru un mijloc fix amortizabil se determină conform următoarelor reguli: a) în cazul construcțiilor, se aplică metoda de amortizare liniară; [...] b) în cazul echipamentelor tehnologice, respectiv al mașinilor, uneltelor și instalațiilor de lucru, precum și pentru computere și echipamente periferice ale acestora, contribuabilul poate opta pentru metoda de amortizare liniară, degresivă sau accelerată; [...] c) în cazul oricărui altui mijloc fix amortizabil, contribuabilul poate opta pentru metoda de amortizare liniară sau degresivă.

— Codul fiscal (Legea 227/2015), art.28 alin.(5)
:::

::: ghid-temei
Nu reprezintă active amortizabile: a) terenurile, inclusiv cele împădurite;

— Codul fiscal (Legea 227/2015), art.28 alin.(4) lit.a)
:::

Practic, categoria unui activ e determinată de contul de imobilizare în care e înregistrat (planul de conturi), care corespunde, la rândul lui, categoriilor din art.28 alin.(5) CF:

| Categorie (cont de imobilizare) | Metode de amortizare permise |
|---|---|
| Construcții (cont 212) | doar liniară |
| Echipamente tehnologice, mașini, unelte, calculatoare (cont 2131) | liniară, degresivă sau accelerată |
| Animale și plantații (conturi 2134/217) | liniară sau degresivă |
| Terenuri (cont 211) | neamortizabile — nu se calculează amortizare deloc |
| Orice alt mijloc fix amortizabil (ex. mobilier, alte instalații) | liniară sau degresivă, **fără** accelerată |

Codul de clasificare ales pentru catalogul HG 2139/2004 (pentru durată) trebuie să corespundă aceleiași categorii reale a activului ca și contul de imobilizare folosit pentru înregistrarea contabilă — cele două clasificări (contabilă și din catalog) descriu, de fapt, aceeași natură a activului, doar din unghiuri diferite (unde se înregistrează, respectiv ce durată/metodă i se aplică).

## Ce se greșește în practică

- Se alege un cont de imobilizare generic sau "cel mai apropiat" fără să se verifice dacă activul se încadrează efectiv în categoria respectivă — o eroare de clasificare poate duce la o metodă de amortizare pe care legea n-o permite pentru activul real.
- Se aplică metoda accelerată unei categorii care n-o permite (ex. mobilier de birou, încadrat la "orice alt mijloc fix" — doar liniară sau degresivă).
- Se tratează un teren ca mijloc fix amortizabil, deși legea îl exclude explicit din categoria activelor amortizabile.

## Ce face iConta.eu

Categoria activului (și, implicit, metodele de amortizare permise) se derivă automat din contul de imobilizare ales la înregistrarea mijlocului fix — nu se introduce separat. Dacă alegeți o metodă de amortizare pe care legea n-o permite pentru categoria rezultată din cont (de exemplu, accelerată pentru un activ înregistrat pe contul de construcții), aplicația **nu calculează tacit o valoare liniară** — rândul respectiv din registru afișează eroare, iar amortizat/rămas rămân necompletate, până corectați metoda sau contul.

[iConta.eu](/)
