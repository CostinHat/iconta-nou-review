---
title: "Ce declarații fiscale trebuie depuse anual în 2026?"
description: "D101 (impozitul pe profit, până la 25 iunie) și D205 (declarația informativă privind reținerea la sursă, până la ultima zi de februarie) sunt cele două declarații cu periodicitate strict anuală, generate automat de iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce declarații fiscale trebuie depuse anual în 2026?

Spre deosebire de declarațiile lunare sau trimestriale, unde periodicitatea depinde adesea de profilul de TVA al firmei, declarațiile anuale au termene fixe, independente de vectorul fiscal: D101 (impozitul pe profit) pentru firmele care plătesc impozit pe profit, și D205 (declarația informativă privind impozitul reținut la sursă) pentru orice firmă care a făcut plăți supuse reținerii la sursă în anul anterior.

## Temeiul legal

::: ghid-temei
„Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Codul fiscal, art. 42 alin. (1) — D101 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„...până în ultima zi a lunii februarie inclusiv a anului curent pentru anul expirat."
— OPANAF 179/2022, cap. I, pct. 5.1 lit. a) — D205 (sursă: anaf_surse/opanaf_179_2022_d205_d207_baza.txt)
:::

Descompus pe declarație:

- **D101** (impozitul pe profit) — obligatorie pentru firmele cu regim de impozit pe profit (nu micro), cu termen 25 iunie anul următor celui de raportare. Firmele care aplică sistemul anual cu plăți anticipate trimestriale (art. 41 alin. 2) depun D101 tot la acest termen, dar plătesc anticipat pe parcursul anului.
- **D205** — declarația informativă privind impozitul reținut la sursă pe beneficiari de venit (dividende, drepturi de autor, alte venituri supuse reținerii), cu termen ultima zi calendaristică a lunii februarie a anului următor celui raportat. Nu e legată de regimul fiscal al firmei (micro sau profit), ci de faptul că firma a efectuat plăți cu reținere la sursă.

Firmele care aplică regimul micro (impozit pe veniturile microîntreprinderilor) nu depun D101 — pentru ele, obligația echivalentă e D100, dar aceasta e trimestrială, nu anuală (vezi ghidul dedicat declarațiilor trimestriale).

## Ce se greșește în practică

- Se confundă D101 cu D100 — D101 e pentru firmele la impozit pe profit, D100 pentru firmele la regimul micro; nu se depun ambele de aceeași firmă în același regim.
- Se presupune că D205 se depune doar de firmele care distribuie dividende — de fapt acoperă orice venit supus reținerii la sursă, nu doar dividendele.
- Se calculează termenul D101 greșit ca „25 martie" (confundat cu vechiul termen al situațiilor financiare) în loc de 25 iunie.
- Se omite depunerea D205 pentru anii în care firma a avut foarte puține plăți cu reținere la sursă, presupunând că declarația „nu se aplică" sub un anumit prag — legea nu prevede un asemenea prag minim.

## Ce face iConta.eu

D101 și D205 fac parte din cele 9 tipuri de declarații pe care iConta.eu le generează prin ecranul „Declarații", parametrizate pe an. Aplicația nu decide singură dacă o firmă e obligată să depună D101 sau D205 — verifică, prin Semaforul de conformare fiscală, dacă profilul firmei (regim fiscal, din Vectorul fiscal) indică obligația, apoi generează formularul completat cu datele contabile introduse pe parcursul anului. Termenele de mai sus (25 iunie pentru D101, ultima zi de februarie pentru D205) sunt calculate automat de motorul intern de scadențe al aplicației, inclusiv mutarea pe următoarea zi lucrătoare dacă data cade într-un weekend sau o sărbătoare legală.

[iConta.eu](/)
