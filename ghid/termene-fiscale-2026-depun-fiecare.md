---
title: "Termene fiscale 2026: când depun fiecare declarație ca să nu iau amendă"
description: Nouă declarații, nouă termene — de la 25 ale lunii următoare, la 30, la ultima zi a lunii, până la 25 iunie anul următor pentru impozitul pe profit.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Termene fiscale 2026: când depun fiecare declarație ca să nu iau amendă

Nu toate declarațiile firmei au același termen — confuzia dintre ele e una dintre cauzele frecvente ale depunerilor cu întârziere. Reperul de bază, 25 ale lunii următoare, se aplică doar unei părți din declarații; celelalte au reguli proprii.

## Temeiul legal

::: ghid-temei
„Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor, cu excepția contribuabililor prevăzuți la art. 41 alin. (16) și (17) care depun declarația anuală privind impozitul pe profit până la termenele prevăzute în cadrul acestor alineate."

*(Codul fiscal — Legea nr. 227/2015, art. 42 alin. (1), formă aplicabilă din anul fiscal 2026, potrivit OUG nr. 8/2026 art. 6 pct. 12)*
:::

## Termenele, declarație cu declarație

- **D100, D112, D300, D390** — 25 ale lunii următoare perioadei de raportare (lunar sau trimestrial, după caz).
- **D394** — 30 ale lunii următoare perioadei de raportare.
- **D406 (SAF-T)** — ultima zi calendaristică a lunii următoare perioadei de raportare (lunar sau trimestrial, în funcție de statutul de TVA).
- **D205** — ultima zi din februarie a anului următor.
- **D101 (impozit pe profit)** — 25 iunie inclusiv a anului următor, conform art. 42 alin. (1) citat mai sus (formă valabilă din anul fiscal 2026; pentru 2021-2025 s-a aplicat același termen, 25 iunie, prin derogare acordată de OUG 153/2020).

Toate aceste termene se mută la prima zi lucrătoare, dacă data calculată pică într-un weekend sau într-o sărbătoare legală (inclusiv Paștele ortodox, cu dată mobilă calculată an de an).

## Ce se greșește în practică

- Se aplică termenul general de „25 ale lunii următoare" și pentru D394 (corect: 30) sau pentru D406 (corect: ultima zi a lunii).
- Se presupune că D101 are termenul clasic de 25 martie — regula s-a schimbat succesiv (OUG 153/2020 pentru 2021-2025, apoi OUG 8/2026 pentru 2026 și următorii), iar termenul actual e 25 iunie anul următor, nu 25 martie.
- Se ignoră mutarea termenului atunci când data calculată pică într-o sărbătoare legală mobilă (Paștele ortodox) — o eroare frecventă când calendarul e calculat „din memorie", nu recalculat anual.

## Ce face iConta.eu

Modulul de scadențe (`core/scadente.py`) calculează, pentru fiecare din cele 9 declarații urmărite, termenul exact al perioadei, mutat automat la prima zi lucrătoare dacă pică în weekend sau sărbătoare legală — inclusiv sărbătorile cu dată mobilă, calculate din data Paștelui ortodox, nu hardcodate an de an. Semaforul F022 (`core/control_fiscal_api.py`) folosește acest calcul ca sursă unică pentru toate verdictele de termen, astfel încât aceeași regulă de scadență se aplică identic în toată aplicația.

[iConta.eu](/)
