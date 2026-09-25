---
title: "Amenda pentru nedepunerea D300 și a D394"
description: "Nedepunerea la termen a decontului de TVA (D300) sau a declarației 394 se sancționează după aceeași regulă din Codul de procedură fiscală, art. 336: 1.000-5.000 lei sau 500-1.000 lei, după mărimea contribuabilului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amenda pentru nedepunerea D300 și a D394

Deși sunt declarații diferite — D300 e decontul de TVA, D394 e o declarație informativă — nedepunerea lor la termen cade sub aceeași prevedere din Codul de procedură fiscală, cu aceleași cuantumuri.

## Temeiul legal

::: ghid-temei
„neîndeplinirea de către contribuabil/plătitor la termen a obligaţiilor de declarare prevăzute de lege, a bunurilor şi veniturilor impozabile sau, după caz, a impozitelor, taxelor, contribuţiilor şi a altor sume, precum şi orice informaţii în legătură cu impozitele, taxele, contribuţiile, bunurile şi veniturile impozabile, dacă legea prevede declararea acestora"
— Legea 207/2015 (Codul de procedură fiscală), art. 336 alin. (1) lit. b) (sursă: anaf_surse/legea_207_2015_consolidat.txt)

„cu amendă de la 1.000 lei la 5.000 lei pentru persoanele juridice încadrate în categoria contribuabililor mijlocii şi mari şi cu amendă de la 500 lei la 1.000 lei, pentru celelalte persoane juridice, precum şi pentru persoanele fizice, în cazul săvârşirii faptei prevăzute la alin. (1) lit. a), b) şi i) - m)"
— Legea 207/2015, art. 336 alin. (2) lit. d) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Amenda e identică pentru cele două declarații, pentru că ambele se încadrează în aceeași literă a contravenției:

- **D300** (decontul de TVA, art. 323 Cod fiscal) e chiar prototipul obligației de „declarare a impozitelor, taxelor... și a altor sume" din art. 336 alin. (1) lit. b).
- **D394** e o declarație informativă creată prin ordin ANAF (OPANAF 2194/2025), care se încadrează în aceeași literă, prin definiția „declarație informativă" de la art. 1 pct. 19 din Codul de procedură fiscală.
- Cuantumul pentru ambele: **1.000–5.000 lei** pentru persoanele juridice încadrate la contribuabili mijlocii/mari, respectiv **500–1.000 lei** pentru celelalte persoane juridice și pentru persoanele fizice.
- Nedepunerea concurentă a ambelor declarații pentru aceeași perioadă nu dublează automat amenda într-un cuantum numit explicit în text — fiecare faptă (fiecare declarație nedepusă) se constată și se sancționează separat de organul fiscal, în limitele de mai sus.

Termenele diferă însă: D300 se depune până pe **25** ale lunii următoare, iar D394 până pe **30** (cu excepția lunii ianuarie: 28/29 februarie) — deci pot exista situații în care una e deja în întârziere, iar cealaltă încă în termen.

## Ce se greșește în practică

- Se presupune că D300 și D394, având termene diferite, au și regim de sancționare diferit — încadrarea contravențională e aceeași (art. 336 alin. (1) lit. b)).
- Se așteaptă un cuantum fix, unic pentru toți contribuabilii — de fapt depinde de categoria contribuabilului (mijlociu/mare vs. restul).
- Se ignoră faptul că fiecare declarație nedepusă e o faptă separată — nedepunerea ambelor pentru aceeași lună nu înseamnă automat o singură amendă „combinată".

## Ce face iConta.eu

Termenele celor două declarații sunt urmărite separat în aplicație (`core/scadente.py`): D300 la ziua 25, D394 la ziua 30 (cu excepția lunii ianuarie). Semaforul de conformare fiscală compară declarațiile datorate, din vectorul fiscal al firmei, cu cele efectiv depuse, pentru ambele.

**iConta.eu nu aplică și nu calculează amenzi** — acestea sunt stabilite exclusiv de organul fiscal, la constatarea contravenției. Aplicația generează și validează local, prin validatorul oficial ANAF (DUK), atât D300, cât și D394, dar depunerea efectivă la termen rămâne responsabilitatea contabilului, prin portalul SPV.

[iConta.eu](/)
