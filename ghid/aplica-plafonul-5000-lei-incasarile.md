---
title: "Cum se aplică plafonul de 5.000 lei la încasările în numerar"
description: "Mecanismul plafonului zilnic de 5.000 lei pentru încasările în numerar de la o firmă, pe zi și pe partener, conform Legii 70/2015."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se aplică plafonul de 5.000 lei la încasările în numerar

Plafonul de 5.000 lei nu se aplică "pe factură" sau "pe zi în total", ci după o formulă precisă: pe zi, pe fiecare persoană/partener în parte, cumulat pe toate operațiunile din ziua respectivă.

## Temeiul legal

::: ghid-temei
„(1) Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: a) încasări de la persoanele prevăzute la art. 1 alin. (1), în limita unui plafon zilnic de 5.000 lei de la o persoană; [...] (2) Sunt interzise încasările fragmentate în numerar de la beneficiari pentru facturile a căror valoare este mai mare de 5.000 lei [...], precum și fragmentarea facturilor pentru o livrare de bunuri sau o prestare de servicii a căror valoare este mai mare de 5.000 lei."
— Legea 70/2015, art. 3 alin. (1) lit. a) și alin. (2) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Formula de calcul, în trei pași:

1. **Unitatea de măsură e ziua calendaristică**, nu tranzacția — toate încasările în numerar de la același partener, în aceeași zi, se **cumulează** pentru verificarea plafonului.
2. **Unitatea de referință e partenerul**, nu firma în ansamblu — plafonul de 5.000 lei se verifică separat pentru fiecare persoană juridică de la care se încasează, nu global pe toate încasările zilei.
3. **Fragmentarea e interzisă separat**, pentru facturi mai mari de 5.000 lei — chiar dacă suma zilnică de la un partener nu depășește plafonul, împărțirea unei singure facturi mari în tranșe de numerar succesive, pe zile diferite, tot încalcă legea, pentru că vizează exact ocolirea plafonului pe acea factură.
4. Excepție de calcul: sumele legate de avansuri spre decontare intră în calculul plafonului zilnic separat, de la data acordării lor (art. 3 alin. (4)), nu la data justificării.

## Ce se greșește în practică

- Se verifică plafonul "pe casă", adică pe totalul încasărilor zilei, indiferent de la cine vin — corect e verificarea separată pe fiecare partener.
- Se ignoră cumulul din aceeași zi când vin mai multe încasări mici de la același partener (ex. două facturi de 3.000 lei fiecare, în aceeași zi) — împreună depășesc plafonul de 5.000 lei și intră sub incidența interdicției.
- Se tratează separat regula de fragmentare pe factură (art. 3 alin. (2)) de plafonul zilnic pe partener (art. 3 alin. (1) lit. a)) — cele două se aplică simultan și independent, iar respectarea uneia nu garantează respectarea celeilalte.

## Ce face iConta.eu

La data acestui ghid, `core/casa.py` implementează exact acest mecanism în funcția `verifica_plafon()`: operațiunile sunt grupate pe zi și pe partener (`defaultdict` cheiat pe partener), sumele se cumulează pentru fiecare persoană juridică în parte, iar depășirea constantei `PLAFON_INCASARE_PJ = Decimal("5000")` generează un avertisment (`PLAFON_INCASARE_PJ`) cu suma găsită și plafonul aplicabil. Verificarea acoperă cumulul zilnic pe partener descris de art. 3 alin. (1) lit. a); interdicția separată de fragmentare pe o singură factură mare (art. 3 alin. (2)) nu e verificată distinct de aplicație.

[iConta.eu](/)
