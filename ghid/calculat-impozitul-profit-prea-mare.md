---
title: "Ce fac dacă am calculat impozitul pe profit prea mare?"
description: "Identifică, pe baza dosarului, cauze documentate ale unei supraevaluări a impozitului pe profit, inclusiv un bug curent al aplicației."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am calculat impozitul pe profit prea mare?

## Temeiul legal

::: ghid-temei
Art.18^1 alin.(16) CF (introdus prin OUG 89/2025 art.I pct.1, MO 1203/24.12.2025, în vigoare 01.01.2026): "Pentru anul fiscal 2026/anul fiscal modificat care începe în anul 2026, cota de impozit din cadrul formulei prevăzute la alin.(3) este 0,5%."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.
:::

Pentru firmele mari (cifră de afaceri anul precedent peste 50.000.000 EUR), o cauză documentată de supraevaluare pentru anul fiscal 2026 este chiar un bug al aplicației: impozitul minim pe cifra de afaceri (IMCA) e calculat cu cota de 1%, deși legea prevede explicit 0,5% pentru 2026 (art.18^1 alin.(16)). O altă cauză posibilă, pentru firme obișnuite, e omiterea unei deduceri legitime (amortizare fiscală P11, rezervă legală P13).

## Ce se greșește în practică

Verificați întâi dacă firma se încadrează la IMCA pentru 2026 — dacă da, impozitul minim generat de aplicație poate fi dublu față de cel legal.

## Ce face iConta.eu

Atenție: motorul D101 din iConta.eu calculează astăzi IMCA cu formula `impozit_minim_cifra_afaceri`, cablată pe cota fixă de 1% (`core/d101.py`, confirmat de testul `test_imca_formula_1pct_din_vt_vs_i_a`), deși legea prevede explicit 0,5% pentru anul fiscal 2026 (art.18^1 alin.(16) CF, introdus prin OUG 89/2025). Dacă firma dvs. se încadrează la IMCA pentru 2026, impozitul minim generat de aplicație poate fi dublu față de cel legal — verificați manual suma până la corectarea acestui bug. Dacă cifra de afaceri a anului precedent (în EUR) transmisă depășește pragul IMCA de 50.000.000 EUR și rândul P47 nu a fost completat manual, iConta.eu cere explicit această valoare înainte de generare — nu subevaluează tacit impozitul unei firme mari. iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`opanaf_206_2025_d101.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
