---
title: "Cum se calculează ajustarea TVA la scoaterea din patrimoniu"
description: "Regula de ajustare a TVA deduse inițial pentru un bun de capital casat sau scos din patrimoniu, inclusiv perioadele de 5 și 20 de ani prevăzute de Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează ajustarea TVA la scoaterea din patrimoniu

Când un mijloc fix pentru care s-a dedus TVA la achiziție este casat sau scos din patrimoniu înainte de finalul perioadei de ajustare, firma nu păstrează automat toată taxa dedusă inițial — legea cere restituirea proporțională a TVA aferente perioadei rămase neconsumate.

## Temeiul legal

::: ghid-temei
„(2) Taxa deductibilă aferentă bunurilor de capital [...] se ajustează, în situațiile prevăzute la alin. (4) lit. a)-d): a) pe o perioadă de 5 ani, pentru bunurile de capital achiziționate sau fabricate, altele decât cele prevăzute la lit. b); b) pe o perioadă de 20 de ani, pentru construcția sau achiziția unui bun imobil, precum și pentru transformarea sau modernizarea unui bun imobil [...].
(4) Ajustarea taxei deductibile [...] se efectuează: [...] d) în situația în care bunul de capital își încetează existența, cu următoarele excepții: [...] 4. în cazul casării unui bun de capital;
(5) [...] d) pentru cazurile prevăzute la alin. (4) lit. d), ajustarea se efectuează în perioada fiscală în care intervine evenimentul care generează ajustarea și se realizează pentru toată taxa aferentă perioadei rămase din perioada de ajustare, incluzând anul în care apare obligația ajustării."
— Legea 227/2015 (Codul fiscal), art. 305 alin. (2), (4) lit. d) pct. 4 și alin. (5) lit. d) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanismul de calcul care rezultă din text:

- **Perioada de ajustare depinde de tipul bunului**: 5 ani pentru bunuri de capital mobile (echipamente, utilaje, mijloace de transport), 20 de ani pentru bunuri imobile (construcții, achiziții/transformări/modernizări de clădiri).
- **Casarea declanșează ajustare integrală pentru perioada rămasă**, nu proporțională pe an — spre deosebire de ajustarea „o cincime/o douăzecime pe an" din alte situații (schimbare de destinație, pro rata), la casare se ajustează dintr-o dată toată taxa aferentă anilor rămași din perioada de ajustare, inclusiv anul curent.
- **Excepțiile care NU declanșează ajustare**: bunul face obiectul unei livrări impozabile (inclusiv livrare către sine, pentru care taxa e deja colectată), bunul e pierdut/distrus/furat cu dovadă corespunzătoare (pentru furt, act al organelor judiciare), sau intră sub incidența art. 270 alin. (8) — situații care, în esență, arată că bunul rămâne în sfera economică taxabilă sau că pierderea nu e imputabilă firmei.
- **Momentul ajustării e evenimentul, nu sfârșitul anului** — ajustarea se face în perioada fiscală în care are loc efectiv casarea, nu se amână la regularizarea de final de an.

## Ce se greșește în practică

- Se aplică regula generală de ajustare „o cincime/o douăzecime pe an" și la casare, deși alin. (5) lit. d) cere ajustarea integrală, dintr-o dată, pentru toți anii rămași din perioada de ajustare, nu eșalonat.
- Se ajustează TVA la casarea unui bun distrus dintr-un incendiu sau furat, fără să se verifice întâi dacă situația se încadrează în excepțiile de la alin. (4) lit. d) pct. 2 — pierderea documentată corespunzător (acte ale organelor judiciare, în cazul furtului) scutește de ajustare.
- Se confundă perioada de ajustare a unui echipament (5 ani) cu cea a unei clădiri (20 de ani), aplicând greșit numărul de ani rămași la calculul sumei de restituit.
- Se amână înregistrarea ajustării până la finalul anului fiscal, deși obligația ia naștere în perioada fiscală în care are loc efectiv casarea.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are în `core/d300.py` rânduri dedicate ajustărilor conform art. 304 (regularizări) și art. 305 (ajustări bunuri de capital) din Codul fiscal, incluse în totalurile decontului. Aceste rânduri se **declară manual** — aplicația nu calculează automat perioada de ajustare rămasă (5 sau 20 de ani, în funcție de tipul bunului) și nu determină singură suma de ajustat la casarea unui mijloc fix. Contabilul trebuie să identifice bunul, perioada de ajustare aplicabilă și anii rămași, apoi să introducă manual valoarea de ajustat în decontul de TVA.

[iConta.eu](/)
