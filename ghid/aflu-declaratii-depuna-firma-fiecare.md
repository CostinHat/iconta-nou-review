---
title: Cum aflu ce declarații trebuie să depună firma mea în fiecare lună?
description: Tiparul lunar de declarații depinde de vectorul fiscal al firmei, nu e același pentru toată lumea — cum îl citești din ecranul Termene al iConta.eu, declarație cu declarație.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum aflu ce declarații trebuie să depună firma mea în fiecare lună?

Nu există un „tipar lunar" universal — ce depune o firmă în fiecare lună depinde de vectorul ei fiscal (regim, statut TVA, tip decont) și de fapte precum existența salariaților. Ecranul „Termene" din iConta.eu îți arată tiparul aplicat firmei tale, nu unul generic.

## Temeiul legal

::: ghid-temei
„sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate"
— Codul fiscal, art. 147 alin. (1) (D112)
:::

Fiecare tip de declarație are propriul ritm, stabilit de propriul act normativ — D112 (citat mai sus) e lunar pentru firmele cu salariați; D300/D390/D406 urmează ritmul TVA (lunar sau trimestrial, după tipul de decont); D100 e trimestrial pentru firmele la regim micro; D101 e anual.

## Cum se compune tiparul lunar al firmei tale

- **Ai salariați?** → D112, în fiecare lună, indiferent de regim sau statut TVA.
- **Ești plătitor de TVA?** → D300 (decontul de TVA) și D406 (SAF-T), în ritmul tipului de decont declarat (lunar sau trimestrial); dacă faci și operațiuni intracomunitare, se adaugă D390, lunar, pe faptul concret al lunii (nu doar pe bifa din vector).
- **Ești neplătitor de TVA?** → D406 se depune totuși, dar trimestrial; dacă ai operațiuni intracomunitare, D301 (nu urmărit pe acest ecran, vezi mai jos).
- **Ești la regim micro?** → D100, trimestrial, indiferent de venituri.
- **Ești la regim de profit?** → doar D101, anual — calendarul din iConta.eu nu îți cere, în acest moment, și declarația trimestrială de impozit pe profit (avansul, cod 103 pe formularul D100); e o limitare cunoscută, nu o confirmare că obligația legală nu există.

Combinând aceste reguli, ecranul „Termene" îți arată exact ce iese din vectorul TĂU fiscal pentru fiecare lună din fereastra de 60 de zile — nu o listă „tipică" de SRL.

## Ce se greșește în practică

- Se presupune un tipar identic pentru toate firmele („orice SRL depune D300, D112, D406 în fiecare lună") — de fapt fiecare declarație depinde de un atribut concret al vectorului fiscal, iar absența lui (neplătitor TVA, fără salariați) elimină declarația corespunzătoare, nu doar o „ascunde".
- Se ignoră faptul că D390 se calculează pe faptul lunii (operațiuni intracomunitare reale), nu doar pe bifa din vectorul fiscal — o lună fără operațiuni nu generează D390, chiar dacă bifa „operațiuni intracomunitare" e activă la firmă.
- Se așteaptă avansul trimestrial de impozit pe profit (cod 103) pe calendar, pentru o firmă la regim de profit — momentan nu apare aici, doar D101 anual.

## Ce face iConta.eu

Ecranul „Termene" recompune tiparul lunar direct din vectorul fiscal completat pentru firmă și din faptele înregistrate (salariați, operațiuni intracomunitare pe lună), folosind același motor de mapare fiscală ca „Semafor". Nu presupune niciodată o declarație implicit datorată — orice atribut necompletat din vector face declarația corespunzătoare să apară „neclar", cu explicația exactă, nu tăcut ca „nu se datorează".

[iConta.eu](/)
