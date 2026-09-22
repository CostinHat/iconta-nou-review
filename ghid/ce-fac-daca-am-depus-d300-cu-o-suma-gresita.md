---
title: Ce fac dacă am depus D300 cu o sumă greșită?
description: Nu se depune un decont rectificativ — D300 nu are acest mecanism; suma greșită se corectează prin rânduri de regularizare (colectate sau deductibile) introduse în decontul perioadei curente sau următoare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce fac dacă am depus D300 cu o sumă greșită?

Descoperirea unei sume greșite într-un D300 deja depus e o situație comună — o factură omisă, o cotă greșită, o sumă transcrisă greșit. Reflexul de a căuta o „rectificativă” nu funcționează pentru TVA: formularul nu are acest mecanism. Corectarea se face prin regularizare, în decontul unei perioade ulterioare.

## Temeiul legal

::: ghid-temei
„Nu se admit întocmirea şi depunerea de deconturi rectificative pentru corectarea datelor
din deconturile anterioare.”
— OPANAF 174/2026, instrucțiuni de completare
:::

## Cum se corectează, în lipsa unei rectificative

Deoarece D300 nu poate fi „refăcut” pentru o lună deja depusă, suma greșită trebuie corectată prin rânduri de regularizare în decontul perioadei curente (sau al primei perioade viitoare în care eroarea e descoperită):

- dacă eroarea a fost pe partea de taxă colectată (de exemplu o livrare omisă sau declarată greșit), se ajustează prin rândurile de regularizare aferente colectatei;
- dacă eroarea a fost pe partea de taxă deductibilă (o achiziție omisă sau dedusă greșit), se ajustează prin rândurile de regularizare aferente deductibilei;
- dacă eroarea a fost la soldul reportat din luna precedentă (rd.38 sau rd.41), se corectează direct în rândul manual corespunzător pentru perioada curentă, cu suma corectă.

Practic, decontul lunii greșite rămâne așa cum a fost depus — diferența se reflectă în lunile următoare, nu retroactiv.

## Ce se greșește în practică

- Se caută o opțiune de „rectificare” a decontului deja depus, care nu există pentru D300.
- Se depune un al doilea decont pentru aceeași lună, în loc să se corecteze prin regularizare în perioada curentă.
- Se lasă eroarea nedeclarată, din lipsa unei căi evidente de corectare, deși regularizarea rezolvă situația legal.
- Se confundă corectarea unei sume greșite pe un rând obișnuit cu corectarea unui sold reportat (rd.38/rd.41) — mecanismul de aplicat diferă în funcție de unde a fost eroarea.

## Ce face iConta.eu

Motorul D300 nu are niciun parametru de tip „decont rectificativ” — nicio cale, în cod, de a regenera sau înlocui un decont deja depus pentru o perioadă trecută. Corectarea unei sume greșite dintr-un decont depus se face prin rândurile de regularizare disponibile în allow-list-ul de rânduri manuale (atât pe partea de colectată, cât și pe partea de deductibilă), introduse în decontul perioadei curente sau al perioadei următoare. Dacă eroarea a fost la soldul reportat din luna precedentă, corectarea se face editând rândul manual corespunzător pentru perioada curentă, nu retroactiv.

[iConta.eu](/)
