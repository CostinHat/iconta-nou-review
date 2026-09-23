---
title: "Cum aleg metoda de amortizare pentru un mijloc fix nou"
description: "Ce metode de amortizare permite legea pe fiecare categorie de mijloc fix și cum le aplică registrul din iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum aleg metoda de amortizare pentru un mijloc fix nou

Alegerea metodei de amortizare nu e liberă — depinde de categoria mijlocului fix, stabilită de contul de imobilizare la care e înregistrat activul.

## Temeiul legal

::: ghid-temei
"Regimul de amortizare pentru un mijloc fix amortizabil se determină conform următoarelor reguli: a) în cazul construcțiilor, se aplică metoda de amortizare liniară; [...] b) în cazul echipamentelor tehnologice, respectiv al mașinilor, uneltelor și instalațiilor de lucru, precum și pentru computere și echipamente periferice ale acestora, contribuabilul poate opta pentru metoda de amortizare liniară, degresivă sau accelerată; [...] c) în cazul oricărui altui mijloc fix amortizabil, contribuabilul poate opta pentru metoda de amortizare liniară sau degresivă." — Codul fiscal, art. 28 alin. (5)
:::

Pe scurt, pe categorii: construcții (cont 212) — doar liniară; echipamente tehnologice (cont 2131) — liniară, degresivă sau accelerată, plus superaccelerată dacă activul e nou și pus în funcțiune în 2026; animale și plantații (cont 2134/217) — liniară sau degresivă, plus superaccelerată dacă e pus în funcțiune în 2026; terenuri (cont 211) — neamortizabile; orice alt mijloc fix (conturi 2132, 2133, 214 sau necunoscut) — liniară sau degresivă, fără accelerată.

## Ce se greșește în practică

Se alege o metodă "pentru că așa a fost la alt activ" fără să se verifice contul de imobilizare al activului curent — de exemplu, se pune accelerată pe un mijloc fix generic, unde legea permite doar liniar sau degresiv.

## Ce face iConta.eu

Câmpul metodă e text liber la import/introducere — aplicația nu blochează alegerea în acel moment. Incompatibilitatea dintre metoda aleasă și categoria activului iese la calculul amortizării: motorul unic verifică metoda față de categoria derivată din contul de imobilizare și, dacă nu e permisă, marchează eroare pe rândul respectiv din registru în loc să calculeze o cifră greșită.

[iConta.eu](/)
