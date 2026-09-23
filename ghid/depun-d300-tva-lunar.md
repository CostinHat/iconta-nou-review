---
title: "Când depun D300 dacă am TVA lunar"
description: Cu perioadă fiscală lunară, D300 se depune și se plătește până la data de 25 a lunii următoare celei pentru care se raportează TVA.
published: 2026-09-25
modified: 2026-09-25
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
- **Luna iunie 2026** → D300 până la 25 iulie 2026.
- **Luna noiembrie 2026** → D300 până la 25 decembrie 2026.
- **Luna decembrie 2026** → D300 până la 25 ianuarie 2027, după aceeași regulă generală.

Notă: instrucțiunile OPANAF 174/2026 mai menționează, separat, și o dată de 21 decembrie (temei art. 155 alin. (2) Cod de procedură fiscală). Sursele verificate pentru acest ghid nu conțin contextul complet al acestei prevederi — nu e confirmat cărei declarații sau perioade i se aplică exact — așa că nu o prezentăm aici ca înlocuind termenul general de 25 ianuarie pentru decontul lunii decembrie. Dacă vă privește această dată, verificați-o punctual în instrucțiunile complete ale formularului sau cu organul fiscal.

## Ce se greșește în practică

- **Se confundă „perioada fiscală lunară" cu depunerea în cursul aceleiași luni** — decontul se depune întotdeauna în luna următoare celei pentru care se raportează, nu în luna curentă.
- **Se presupune un termen diferit pentru plată față de depunere** — pentru TVA, cele două coincid, la 25 a lunii următoare.
- **Se aplică automat data de 21 decembrie din OPANAF 174/2026 la decontul lunar obișnuit**, fără verificarea contextului exact al acelei prevederi — sursele verificate pentru acest ghid nu confirmă că data respectivă înlocuiește termenul general.

## Ce face iConta.eu

Decontul de TVA v12 (`core/d300.py`) determină automat perioada fiscală lunară a firmei (`core/perioada_fiscala_tva.py`) și calculează TVA de plată/recuperat conform structurii OPANAF 174/2026, valabilă din prima perioadă fiscală a anului 2026.

[iConta.eu](/)
