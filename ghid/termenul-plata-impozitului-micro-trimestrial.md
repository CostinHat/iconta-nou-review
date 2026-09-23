---
title: "Termenul de plată a impozitului micro trimestrial"
description: "Termenul legal de plată și declarare a impozitului pe veniturile microîntreprinderilor, cu excepția de la trimestrul IV și modul în care iConta.eu generează D100."
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

Pentru primele trei trimestre, calculul e simplu: trimestrul I se declară până pe 25 aprilie, trimestrul II până pe 25 iulie, trimestrul III până pe 25 octombrie.

**Excepție la trimestrul IV:** deși varianta „clasică” a regulii ar da 25 ianuarie anul următor, sursele oficiale ANAF folosite de validatorul de declarații indică pentru trimestrul IV termenul **25 iunie anul următor**, nu 25 ianuarie. Regula veche (25 ianuarie) a fost valabilă „până în anul 2025 inclusiv”, dar comportamentul curent al validatorului oficial (verificat pe date din 2026) respinge 25 ianuarie pentru trimestrul IV.

## Ce se greșește în practică

- Se presupune că trimestrul IV se declară tot pe 25 ianuarie anul următor, ca celelalte trimestre — regula s-a schimbat, iar o declarație depusă cu acest termen vechi poate fi respinsă de validatorul oficial.
- Se confundă impozitul micro cu un mecanism de „plăți anticipate” — impozitul micro nu are componentă de anticipare, se calculează direct pe veniturile trimestrului și se declară/plătește definitiv la termenul de mai sus.

## Ce face iConta.eu

Pentru firmele la regim micro, aplicația calculează impozitul din veniturile contabilizate (clasele de conturi de venituri) înmulțite cu cota aplicabilă, generează D100 cu cod obligație 121 și atributul obligatoriu `cota="1"` (cota unică din 2026), pe contul bugetar unic 5503XXXXXX.

Pentru scadența trimestrului IV, aplicația respectă termenul de 25 iunie anul următor, conform comportamentului validatorului oficial, nu regula veche de 25 ianuarie.

O particularitate de reținut: dacă într-un trimestru nu rezultă nicio obligație de plată (venituri contabilizate = 0), aplicația nu generează declarația D100 pentru acel trimestru, deoarece structura XML cerută de sistemul de validare impune cel puțin o secțiune de obligație completată, iar una „pe zero” e respinsă structural.

[iConta.eu](/)
