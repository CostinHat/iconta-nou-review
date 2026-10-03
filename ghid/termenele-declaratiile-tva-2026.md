---
title: "Termenele pentru declarațiile de TVA în 2026"
description: Termenul general pentru D300 e 25 a lunii următoare încheierii perioadei fiscale (lunar sau trimestrial), mutat în prima zi lucrătoare dacă pică într-o zi nelucrătoare. Excepție: decontul cu termen la 25 decembrie (luna noiembrie) se depune până la 21 decembrie.
published: 2026-09-25
modified: 2026-10-03
poarta: v1
---

# Termenele pentru declarațiile de TVA în 2026

Termenul de depunere a D300 depinde de perioada fiscală aleasă (lunară sau trimestrială), dar regula de bază e aceeași pentru toată lumea: 25 a lunii care urmează încheierii perioadei. Excepția privește termenul care s-ar împlini la 25 decembrie: decontul lunii noiembrie (perioadă lunară) se depune până la 21 decembrie, iar dacă 21 decembrie e zi nelucrătoare, până în ultima zi lucrătoare dinaintea ei (Codul de procedură fiscală art. 155 alin. (2), reluat în instrucțiunile OPANAF 174/2026). Decontul lunii decembrie urmează regula generală: 25 ianuarie.

## Temeiul legal

::: ghid-temei
**Art. 323 alin. (1) Cod fiscal (Legea 227/2015):** *„... trebuie să depună ... un decont de taxă, până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală respectivă."*

**OPANAF 174/2026, Anexa 2 (Instrucțiuni):**
- lit. a) — lunar: *„până la data de 25 inclusiv a lunii următoare celei pentru care se depune decontul... perioada fiscală este luna calendaristică, potrivit prevederilor art. 322 din Codul fiscal"*.
- lit. b) — trimestrial: *„până la data de 25 inclusiv a primei luni din trimestrul următor... potrivit prevederilor art. 322 din Codul fiscal"*.
- Excepție 25 decembrie: *„se depune... până la data de 21 decembrie"* (temei art. 155 alin. (2) Cod procedură fiscală).
:::

## Termenele concrete

- **Perioadă fiscală lunară** — D300 se depune până la data de 25 a lunii următoare. Exemplu: pentru luna martie 2026, termenul e 25 aprilie 2026.
- **Perioadă fiscală trimestrială** — D300 se depune până la data de 25 a primei luni din trimestrul următor. Exemplu: pentru trimestrul I 2026, termenul e 25 aprilie 2026.
- **21 decembrie**: Excepția privește termenul care s-ar împlini la 25 decembrie: decontul lunii noiembrie (perioadă lunară) se depune până la 21 decembrie, iar dacă 21 decembrie e zi nelucrătoare, până în ultima zi lucrătoare dinaintea ei (Codul de procedură fiscală art. 155 alin. (2), reluat în instrucțiunile OPANAF 174/2026). Decontul lunii decembrie urmează regula generală: 25 ianuarie.
- Instrucțiunile OPANAF 174/2026 mai prevăd și cazuri de excepție (semestrial/anual, aprobate individual de organul fiscal) și o regulă specială pentru achizițiile intracomunitare care schimbă exigibilitatea în cazul plătitorilor trimestriali.

Termenul e comun pentru declarare și plată — data de 25 e atât data limită de depunere a decontului, cât și data limită de plată a TVA rezultate.

## Ce se greșește în practică

- **Se aplică data de 21 decembrie oricărui decont depus în decembrie, sau, invers, termenul de 25 decembrie decontului lunii noiembrie.** Excepția privește doar termenul care s-ar împlini la 25 decembrie (decontul lunii noiembrie); decontul lunii decembrie se depune până la 25 ianuarie.
- **Se confundă perioada fiscală cu data de depunere** — perioada fiscală e intervalul pentru care se calculează TVA (luna sau trimestrul), iar termenul de depunere e întotdeauna în luna următoare, nu în interiorul perioadei.
- **Se presupune că termenul de plată e diferit de termenul de depunere** — pentru TVA, cele două coincid, la aceeași dată.

## Ce face iConta.eu

Decontul de TVA v12 din aplicație (`core/d300.py`) calculează TVA de plată/recuperat pentru perioada fiscală selectată, lunară sau trimestrială, conform structurii OPANAF 174/2026, valabilă pentru declararea obligațiilor aferente primei perioade fiscale din 2026. Determinarea perioadei fiscale (lunar/trimestrial) și avertismentele pentru situații atipice (cote neobișnuite, rezultat neașteptat) sunt gestionate direct în modul.

[iConta.eu](/)
