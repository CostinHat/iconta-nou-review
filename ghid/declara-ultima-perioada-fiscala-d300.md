---
title: "Cum se declară ultima perioadă fiscală în D300?"
description: Ultima perioadă fiscală de TVA se declară după regula generală de termen, dar cu o particularitate practică — dacă rezultă sumă negativă, nu mai există o perioadă următoare în care să o reportezi, deci rămâne relevantă doar solicitarea de rambursare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se declară ultima perioadă fiscală în D300?

Sursele verificate pentru acest ghid nu conțin o regulă specială de depunere pentru „ultima perioadă fiscală" a unei firme (de exemplu, cea dinaintea radierii din scopuri de TVA) — decontul respectiv se depune după aceeași regulă generală ca oricare altul. Ce se schimbă e ce faci cu un eventual sold negativ, pentru că nu mai există o perioadă următoare în care să-l reportezi.

## Temeiul legal

::: ghid-temei
**Art. 323 alin. (1) Cod fiscal (Legea 227/2015):** *„... trebuie să depună ... un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă."*

**Art. 303 alin. (7) Cod fiscal** — dreptul de a alege între rambursare și reportare: *„Persoanele impozabile... pot solicita rambursarea soldului sumei negative... prin bifarea casetei corespunzătoare din decontul de taxă... sau pot reporta soldul... în decontul perioadei fiscale următoare... Nu poate fi solicitată rambursarea soldului sumei negative... mai mic de 5.000 lei inclusiv, acesta fiind reportat obligatoriu..."*
:::

## Ce e diferit la ultima perioadă

Termenul de depunere rămâne cel general — 25 a lunii următoare încheierii perioadei fiscale respective (art. 323 alin. (1)) — indiferent dacă e sau nu ultima perioadă declarată de firmă.

Diferența practică apare dacă decontul respectiv iese cu **sumă negativă** de TVA. În mod normal, o sumă negativă sub 5.000 lei se reportează obligatoriu în decontul perioadei următoare (art. 303 alin. (7)). Dar dacă nu mai există o „perioadă fiscală următoare" (firma se lichidează sau se radiază din scopuri de TVA), reportarea nu mai e o opțiune reală — rămâne doar solicitarea rambursării, prin bifarea casetei corespunzătoare din decont, indiferent de sumă.

Sursele verificate nu conțin o regulă explicită care să elimine pragul de 5.000 lei în acest caz special — recomandăm verificarea situației concrete cu organul fiscal sau cu un consultant, dacă suma negativă a ultimei perioade e sub acest prag.

## Ce se greșește în practică

- **Se lasă soldul negativ „reportat"**, deși nu va mai exista un decont ulterior în care să fie preluat — dacă e ultima perioadă, opțiunea de reportare rămâne fără efect practic.
- **Se presupune un termen de depunere diferit pentru ultima perioadă** — termenul general (25 a lunii următoare) se aplică și aici, sursele verificate nu conțin o excepție.
- **Se omite bifarea casetei de rambursare**, din obișnuința de a reporta soldul negativ, ca la orice altă perioadă.

## Ce face iConta.eu

Decontul de TVA v12 (`core/d300.py`) calculează corect soldul sumei negative/de plată la finalul perioadei (R33-R42), inclusiv reportarea soldului din perioada precedentă. Aplicația nu automatizează alegerea între rambursare și reportare — bifarea casetei corespunzătoare din decont rămâne o decizie manuală, făcută de contabil la depunerea în SPV, cu atât mai importantă la ultima perioadă fiscală declarată.

[iConta.eu](/)
