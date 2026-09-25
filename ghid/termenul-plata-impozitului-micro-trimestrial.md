---
title: "Termenul de plată a impozitului micro trimestrial"
description: "Termenul legal de plată și declarare a impozitului pe veniturile microîntreprinderilor — 25 inclusiv a lunii următoare fiecărui trimestru, inclusiv 25 ianuarie pentru trimestrul IV — și modul în care iConta.eu generează D100."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Termenul de plată a impozitului micro trimestrial

Impozitul pe veniturile microîntreprinderilor se calculează și se declară trimestrial, prin declarația unică D100 (cod obligație 121). Termenul e fixat de lege la nivel de trimestru, dar are o particularitate importantă la trimestrul IV.

## Temeiul legal

::: ghid-temei
„Calculul și plata impozitului pe veniturile microîntreprinderilor se efectuează trimestrial, până la data de 25 inclusiv a lunii următoare trimestrului pentru care se calculează impozitul.” — Codul fiscal (Legea 227/2015), art. 56 alin. (1)
:::

Aceeași dată guvernează și depunerea declarației: potrivit art. 56 alin. (2), „Microîntreprinderile au obligația de a depune, până la termenul de plată a impozitului, declarația de impozit pe veniturile microîntreprinderilor.” Practic, plata și depunerea D100 au același termen.

Nomenclatorul declarației D100 (OPANAF 587/2016) confirmă acest lucru: poziția 5, cod obligație 121, „Impozit pe veniturile microîntreprinderilor”, cu perioadă de raportare „T” (trimestrial).

Regula e uniformă pentru toate cele patru trimestre: trimestrul I se declară până pe 25 aprilie, trimestrul II până pe 25 iulie, trimestrul III până pe 25 octombrie, iar trimestrul IV până pe **25 ianuarie anul următor** — „25 inclusiv a lunii următoare trimestrului", conform art. 56 alin. (1).

Termenul de 25 iunie pe care unele surse îl asociau cu trimestrul IV venea din OUG 153/2020 (art. I alin. (13) lit. b)), o facilitate limitată prin art. VI la perioada 2021–2025. Pentru trimestrul IV 2026 nu mai e aplicabil: termenul este 25 ianuarie 2027.

## Ce se greșește în practică

- Se aplică pentru trimestrul IV 2026 termenul de 25 iunie, preluat din facilitatea OUG 153/2020 care a expirat la finalul anului 2025 — termenul corect, potrivit art. 56 alin. (1), este 25 ianuarie anul următor.
- Se confundă impozitul micro cu un mecanism de „plăți anticipate” — impozitul micro nu are componentă de anticipare, se calculează direct pe veniturile trimestrului și se declară/plătește definitiv la termenul de mai sus.

## Ce face iConta.eu

Pentru firmele la regim micro, aplicația calculează impozitul din veniturile contabilizate (clasele de conturi de venituri) înmulțite cu cota aplicabilă, generează D100 cu cod obligație 121 și atributul obligatoriu `cota="1"` (cota unică din 2026), pe contul bugetar unic 5503XXXXXX.

Pentru scadența trimestrului IV, aplicația respectă termenul de 25 ianuarie anul următor, potrivit art. 56 alin. (1) din Codul fiscal.

O particularitate de reținut: dacă într-un trimestru nu rezultă nicio obligație de plată (venituri contabilizate = 0), aplicația nu generează declarația D100 pentru acel trimestru, deoarece structura XML cerută de sistemul de validare impune cel puțin o secțiune de obligație completată, iar una „pe zero” e respinsă structural.

[iConta.eu](/)
