---
title: "Termenul maxim de finalizare a inspecției fiscale"
description: "Duratele maxime legale ale unei inspecții fiscale, diferențiate pe categorii de contribuabili, conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Termenul maxim de finalizare a inspecției fiscale

Inspecția fiscală nu poate dura la nesfârșit — legea îi impune organului de inspecție un termen maxim, diferențiat în funcție de mărimea contribuabilului controlat.

## Temeiul legal

::: ghid-temei
„ART. 126 Durata efectuării inspecției fiscale
(1) Durata efectuării inspecției fiscale este stabilită de organul de inspecție fiscală, în funcție de obiectivele inspecției, și nu poate fi mai mare de:
a) 180 de zile pentru contribuabilii mari, pentru contribuabilii/plătitorii care au sedii secundare, indiferent de mărime, precum și pentru contribuabilii nerezidenți;
b) 90 de zile pentru contribuabilii mijlocii;
c) 45 de zile pentru ceilalți contribuabili."
— Legea 207/2015 (Codul de procedură fiscală), art. 126 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Câteva precizări care rezultă din textul legal și din articolele conexe:

- Termenele maxime sunt **diferențiate pe categorii de contribuabil**: 180 de zile pentru contribuabilii mari, cei cu sedii secundare (indiferent de mărime) și nerezidenți; 90 de zile pentru contribuabilii mijlocii; 45 de zile pentru toți ceilalți.
- Aceste termene sunt **maxime**, nu fixe — organul de inspecție stabilește durata efectivă în funcție de obiectivele controlului, în limita plafonului legal pentru categoria contribuabilului.
- Termenul poate fi **suspendat** legal, în situații expres prevăzute (art. 127) — de exemplu, pentru efectuarea de controale încrucișate, expertize, solicitări de informații de la autorități sau terți, sau verificări la ceilalți membri ai unui grup fiscal. Perioada de suspendare nu se include în termenul maxim.
- În caz de încetare a persoanei juridice controlate în timpul inspecției, controlul continuă cu succesorii, dacă există, sau încetează dacă aceștia nu există.

## Ce se greșește în practică

- Se calculează termenul maxim uniform (de exemplu, mereu 45 de zile), fără să se verifice dacă firma controlată intră în categoria contribuabililor mari/mijlocii sau are sedii secundare, ceea ce schimbă complet plafonul aplicabil.
- Se confundă durata inspecției cu termenul de la începerea controlului până la comunicarea deciziei de impunere, deși acestea nu coincid întotdeauna — decizia poate fi comunicată la scurt timp după încheierea efectivă a inspecției.
- Se ignoră perioadele de suspendare legală, considerând că termenul curge continuu de la începutul până la finalul controlului.

## Ce face iConta.eu

Am verificat în `core/control_fiscal_api.py` și modulele conexe (`core/alerte_control_fiscal.py`, `core/control_incrucisat.py`): aplicația construiește un semafor de conformare fiscală care compară declarațiile datorate cu cele depuse, dar **nu urmărește durata unei inspecții fiscale în curs** — nu există în cod o funcție care să calculeze sau să alerteze la apropierea termenului maxim de 180/90/45 de zile prevăzut de art. 126 din Codul de procedură fiscală. Urmărirea acestui termen, inclusiv verificarea eventualelor suspendări, rămâne responsabilitatea contribuabilului sau a consultantului fiscal implicat în control.

[iConta.eu](/)
