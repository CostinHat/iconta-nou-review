---
title: "Ce faci dacă ai omis o cheltuială deductibilă din D101?"
description: "Explică efectul omiterii unei cheltuieli deductibile (de exemplu amortizarea fiscală) și limita curentă de corectare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce faci dacă ai omis o cheltuială deductibilă din D101?

## Temeiul legal

::: ghid-temei
Art.42 alin.(1) CF (modificat prin OUG 8/2026 art.6 pct.12, MO 147/25.02.2026, aplicabil începând cu anul fiscal 2026): "Contribuabilii au obligația să depună o declarație anuală privind impozitul pe profit până la data de 25 iunie inclusiv a anului următor..."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `anaf_surse/d101_scadenta_conflict_lege_validator.md` + `core/d101.py` (liniile 193-232), dosar de cercetare F027.
:::

În D101, deducerile precum amortizarea fiscală se introduc manual, la rândul P11, și reduc profitul impozabil prin includerea în P16 (total deduceri). Omiterea unei astfel de cheltuieli deductibile duce la un impozit pe profit declarat mai mare decât cel real datorat.

## Ce se greșește în practică

Greșeala tipică e omiterea integrală a amortizării fiscale la P11, mai ales când contabilul introduce doar cheltuiala contabilă cu amortizarea (care se tratează diferit, ca add-back în P28/P34) și uită deducerea fiscală propriu-zisă.

## Ce face iConta.eu

D101 tratează amortizarea ca intrare, nu o calculează: P11 este amortizarea fiscală (deducere — intră în P16, total deduceri, și reduce profitul impozabil), iar rândurile de tip P2x/P28 reprezintă cheltuiala cu amortizarea contabilă, care intră în rollup-ul P34 „cheltuieli nedeductibile” și se adaugă înapoi la baza impozabilă. Contabilul introduce manual ambele valori în iConta.eu. iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`d101_struct_anaf.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
