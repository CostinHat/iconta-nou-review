---
title: Cine are obligația să depună D101?
description: D101 e declarația anuală de impozit pe profit — o depun persoanele juridice aflate pe acest regim, niciodată firmele pe microîntreprindere sau PFA-urile cu partidă simplă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cine are obligația să depună D101?

D101 e declarația anuală privind impozitul pe profit — obligația de a o depune ține strict de regimul fiscal al firmei, nu de mărimea ei sau de alte criterii. O firmă pe microîntreprindere nu depune D101, ci D100; o firmă pe impozit pe profit depune D101, nu D100.

## Temeiul legal

::: ghid-temei
„Sunt obligate la plata impozitului pe profit, conform prezentului titlu, următoarele persoane, denumite în continuare contribuabili: a) persoanele juridice române, cu excepțiile prevăzute la alin. (2)..."

*(Codul fiscal — Legea nr. 227/2015, art. 13 alin. (1) lit. a))*
:::

Obligația de a **depune declarația** decurge din calitatea de contribuabil plătitor de impozit pe profit, stabilită la art. 13: „Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor" (art. 42 alin. (1) CF, formă aplicabilă din anul fiscal 2026).

## Cine depune, practic

- **Persoanele juridice române aflate pe regim de impozit pe profit** (nu pe microîntreprindere) — categoria principală, art. 13 alin. (1) lit. a).
- **Persoanele juridice străine cu sediu permanent în România**, persoanele juridice străine rezidente fiscal în România și alte categorii enumerate la art. 13 alin. (1) — cazuri mai puțin frecvente pentru o firmă românească obișnuită.

## Cine NU depune D101

- **Firmele pe regim de microîntreprindere** — depun D100, trimestrial, nu D101.
- **PFA, întreprinderi individuale, întreprinderi familiale (partidă simplă)** — nu sunt persoane juridice plătitoare de impozit pe profit; impozitul pe venitul lor se declară prin Declarația unică (D212), nu prin D101 sau D100.

## Ce se greșește în practică

- Se presupune că orice SRL depune automat D101, indiferent de regimul fiscal — o firmă pe microîntreprindere depune D100, nu D101.
- Se confundă D101 cu declarația anuală a unei firme pe partidă simplă — PFA/II/IF nu au niciodată obligația de D101, indiferent de venit.
- Se așteaptă apariția obligației de D101 din prima lună de activitate — e o declarație anuală, pentru anul fiscal încheiat, nu una curentă.

## Ce face iConta.eu

Semaforul de conformare fiscală (F022, `core/control_fiscal_api.py`) decide automat între D100 și D101 pe baza regimului fiscal completat în profilul firmei: „micro" generează urmărirea D100 (trimestrial), „profit" generează urmărirea D101, pentru anul precedent, cu termenul calculat conform art. 42 CF. Firmele pe partidă simplă (PFA/II/IF) sunt excluse explicit de la ambele — motorul le marchează „nu se datorează", nu „nedepus", cu motivul: impozitul pe profit e al persoanelor juridice, iar impozitul pe venitul PFA se depune prin Declarația unică (D212). Dacă regimul fiscal nu e completat în profilul firmei, semaforul nu poate decide între D100 și D101 și marchează starea „nu se poate verifica", nu implicit una dintre cele două.

[iConta.eu](/)
