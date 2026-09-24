---
title: "Ce faci dacă pierderea fiscală din D101 a fost declarată greșit?"
description: "Explică onest limitarea curentă a aplicației privind corectarea unei D101 cu pierdere fiscală declarată greșit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce faci dacă pierderea fiscală din D101 a fost declarată greșit?

## Temeiul legal

::: ghid-temei
Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

O pierdere fiscală declarată greșit în D101 e, ca orice altă eroare din declarație, o problemă de rectificare a D101 deja depuse. Sursele verificate în acest dosar nu conțin un temei normativ local dedicat procedurii de rectificare a D101 — doar flagul `d_rec` din structura XML oficială confirmă că formularul o prevede la nivel de format.

## Ce se greșește în practică

Se greșește prin amânarea corectării sau prin încercarea de a o rezolva prin ajustarea manuală a declarației viitoare, ceea ce nu corectează anul deja depus greșit.

## Ce face iConta.eu

iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`opanaf_206_2025_d101.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
