---
title: "Cum se depune D101 rectificativă?"
description: "Explică onest ce prevede formularul oficial și ce nu acoperă în prezent aplicația privind rectificativa D101."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se depune D101 rectificativă?

## Temeiul legal

::: ghid-temei
Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

Formularul oficial D101 (structura reconstruită după OPANAF 206/2025) conține flagul `d_rec`, care indică faptul că ANAF prevede, la nivel de format, o variantă rectificativă a declarației. Sursele legale locale verificate pentru acest dosar nu conțin însă un act normativ dedicat care să detalieze procedura exactă (cine poate rectifica, termene, documente anexă) pentru D101 — acest gol de temei trebuie completat direct din instrucțiunile ANAF sau cu un consultant fiscal.

## Ce se greșește în practică

Greșeala frecventă e presupunerea că depunerea rectificativă se poate iniția din iConta.eu, la fel ca la D100.

## Ce face iConta.eu

iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`d101_struct_anaf.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
