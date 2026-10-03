---
title: "Când depun D300 dacă am TVA lunar"
description: Cu perioadă fiscală lunară, D300 se depune și se plătește până la data de 25 a lunii următoare celei pentru care se raportează TVA.
published: 2026-09-25
modified: 2026-10-03
poarta: v1
---

# Când depun D300 dacă am TVA lunar

Pentru un plătitor cu perioadă fiscală lunară, termenul e simplu: data de 25 a lunii care urmează lunii pentru care se calculează TVA. Aceeași dată e și termenul de plată.

## Temeiul legal

::: ghid-temei
**Art. 323 alin. (1) Cod fiscal (Legea 227/2015):** *„... trebuie să depună ... un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă."*

**OPANAF 174/2026, Anexa 2 lit. a):** *„până la data de 25 inclusiv a lunii următoare celei pentru care se depune decontul... perioada fiscală este luna calendaristică, potrivit prevederilor art. 322 din Codul fiscal."*
:::

## Termenul, cu exemple

- **Luna ianuarie 2026** → D300 până la 25 februarie 2026.
- **Luna iunie 2026** → D300 până la 27 iulie 2026 (25 iulie e sâmbătă; termenul se prelungește până în prima zi lucrătoare — Codul de procedură fiscală art. 75 și Codul de procedură civilă art. 181 alin. (2)).
- **Luna noiembrie 2026** → D300 până la 21 decembrie 2026 (Codul de procedură fiscală art. 155 alin. (2): termenul care s-ar împlini la 25 decembrie se împlinește la 21 decembrie).
- **Luna decembrie 2026** → D300 până la 25 ianuarie 2027, după aceeași regulă generală.

Notă: excepția de la 21 decembrie privește doar termenul care s-ar împlini la 25 decembrie, adică decontul lunii noiembrie; dacă 21 decembrie e zi nelucrătoare, termenul e ultima zi lucrătoare dinaintea ei (Codul de procedură fiscală art. 155 alin. (2), reluat în instrucțiunile OPANAF 174/2026). Decontul lunii decembrie urmează regula generală, 25 ianuarie.

## Ce se greșește în practică

- **Se confundă „perioada fiscală lunară" cu depunerea în cursul aceleiași luni** — decontul se depune întotdeauna în luna următoare celei pentru care se raportează, nu în luna curentă.
- **Se presupune un termen diferit pentru plată față de depunere** — pentru TVA, cele două coincid, la 25 a lunii următoare.
- **Se aplică termenul de 25 decembrie decontului lunii noiembrie**, deși el se depune până la 21 decembrie; sau, invers, data de 21 decembrie se aplică și decontului lunii decembrie, care se depune până la 25 ianuarie.

## Ce face iConta.eu

Decontul de TVA v12 (`core/d300.py`) determină automat perioada fiscală lunară a firmei (`core/perioada_fiscala_tva.py`) și calculează TVA de plată/recuperat conform structurii OPANAF 174/2026, valabilă din prima perioadă fiscală a anului 2026.

[iConta.eu](/)
