---
title: "Când se depune ultima D300 la lichidarea firmei?"
description: Sursele verificate pentru acest ghid nu conțin un termen special pentru ultimul decont de TVA la lichidare — termenul rămâne cel general, 25 a lunii următoare încheierii perioadei fiscale în care are loc radierea din scopuri de TVA.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Când se depune ultima D300 la lichidarea firmei?

La lichidarea unei firme, ultimul decont de TVA nu are, în sursele verificate pentru acest ghid, un termen accelerat sau diferit — se depune după aceeași regulă generală ca oricare alt decont, pentru perioada fiscală în care firma a fost radiată din scopuri de TVA.

## Temeiul legal

::: ghid-temei
**Art. 323 alin. (1) Cod fiscal (Legea 227/2015):** *„... trebuie să depună ... un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă."*
:::

## Ce e confirmat și ce nu

Confirmat: termenul general de depunere e 25 a lunii următoare încheierii perioadei fiscale respective. Dacă firma se radiază din scopuri de TVA în cursul unei luni (sau al unui trimestru, pentru plătitorii trimestriali), acea perioadă — de la începutul ei până la data radierii — devine ultima perioadă fiscală pentru care se depune decont, cu termen de depunere tot la 25 a lunii următoare.

Neconfirmat în sursele verificate: dacă legislația prevede un termen scurtat, specific momentului lichidării/radierii (de exemplu, un termen legat direct de data radierii, nu de calendarul obișnuit lunar/trimestrial). Nu am identificat, în corpusul verificat pentru acest ghid, un asemenea termen special — de aceea nu îl afirmăm aici. Recomandăm verificarea acestui aspect cu organul fiscal sau cu un consultant, în special dacă radierea nu coincide cu finalul unei perioade fiscale calendaristice complete.

Un aspect conex, confirmat: dacă ultimul decont iese cu sumă negativă de TVA, nu mai există o perioadă fiscală următoare în care soldul să fie reportat — rămâne relevantă solicitarea rambursării (art. 303 alin. (7) Cod fiscal), prin bifarea casetei corespunzătoare din decont.

## Ce se greșește în practică

- **Se presupune că lichidarea impune un termen mai scurt de depunere a ultimului D300** — sursele verificate nu confirmă un asemenea termen special; se aplică regula generală de 25 a lunii următoare.
- **Se lasă soldul negativ al ultimului decont „reportat"**, deși nu va mai exista o perioadă ulterioară care să-l preia — la lichidare, rambursarea rămâne opțiunea practică.
- **Se depune ultimul decont fără coordonare cu data efectivă a radierii din scopuri de TVA** — perioada fiscală finală trebuie să corespundă exact intervalului cât firma a fost înregistrată în scopuri de TVA.

## Ce face iConta.eu

Decontul de TVA v12 (`core/d300.py`) calculează TVA de plată/recuperat pentru orice perioadă fiscală selectată, inclusiv una parțială, pe baza operațiunilor înregistrate. Aplicația nu are un flux dedicat, separat, pentru „ultimul decont la lichidare" — perioada finală se tratează ca orice altă perioadă fiscală, cu atenția suplimentară, la sold negativ, că rambursarea rămâne singura opțiune practică, nu reportarea.

[iConta.eu](/)
