---
title: Ce taxe se plătesc pentru indemnizația administratorului?
description: CAS 25%, CASS 10% și impozit 10% pe ce rămâne, plus contribuția asiguratorie pentru muncă (CAM 2,25%) datorată de societate — remunerația administratorului e inclusă în baza CAM prin art. 220^4 alin. (1) lit. d) din Codul fiscal.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce taxe se plătesc pentru indemnizația administratorului?

Indemnizația plătită administratorului cu contract de mandat e un venit asimilat salariilor: se rețin CAS, CASS și impozit pe venit, iar societatea datorează și contribuția asiguratorie pentru muncă (CAM), pentru că remunerația administratorului e inclusă expres în baza de calcul a CAM (Codul fiscal art. 220^4 alin. (1) lit. d)).

## Temeiul legal

::: ghid-temei
„remunerația administratorilor societăților, companiilor/societăților naționale și regiilor autonome, desemnați/numiți în condițiile legii, precum și sumele primite de reprezentanții în adunarea generală a acționarilor și în consiliul de administrație"

*(Codul fiscal — Legea nr. 227/2015, art. 76 alin. (2) lit. o))*
:::

## Ce se reține din indemnizație

Din indemnizația brută se calculează, în această ordine:
1. **CAS 25%** pe brut.
2. **CASS 10%** pe brut.
3. **Impozit pe venit 10%** pe baza rămasă (brut − CAS − CASS).

**Se datorează și CAM** (contribuția asiguratorie pentru muncă, 2,25%) — o contribuție a societății, nu reținută din indemnizație. Codul fiscal art. 220^4 alin. (1) lit. d) include expres în baza de calcul a CAM „remunerația administratorilor societăților, companiilor/societăților naționale și regiilor autonome, desemnați/numiți în condițiile legii", iar lit. e) remunerația directorilor cu contract de mandat. Faptul că mandatul nu e un raport de muncă în sensul Codului muncii nu îl scoate din baza CAM, pentru că legea îl enumeră distinct.

## Ce se greșește în practică

- **Se citează art. 76 alin. (2) lit. g) drept temei** pentru remunerația administratorului — lit. g) e despre președintele asociației de proprietari (Legea 230/2007), nu despre administratorul unei societăți. Temeiul corect pentru administrator e **lit. o)**.
- **Se omite CAM** pe motiv că administratorul de mandat nu are raport de muncă — greșit: remunerația administratorilor și a directorilor cu contract de mandat e inclusă expres în baza CAM (art. 220^4 alin. (1) lit. d) și e)).
- **Se confundă administratorul cu mandat cu cenzorul** — deși calculul (CAS+CASS+impozit, fără CAM) e identic ca structură, temeiul fiscal e diferit: lit. o) pentru administrator, **lit. i)** pentru cenzor.

## Ce face iConta.eu

Funcția `calcul_mandat(brut)` din modulul F021 (`core/contracte_speciale.py`) aplică exact această structură — CAS 25% + CASS 10% + impozit 10% pe (brut − CAS − CASS), fără CAM — pentru ambele cazuri, mandat de administrator și cenzor. Notă: docstring-ul modulului citează generic „CF art. 76(2) lit. g/i" pentru cele două cazuri; verificarea la sursă arată că lit. g) nu e temeiul corect pentru administrator — temeiul corect e lit. o), care nu apare în comentariul din cod, deși calculul aplicat e cel corect.

[iConta.eu](/)
