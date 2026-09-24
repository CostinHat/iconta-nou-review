---
title: "Ce faci dacă ai declarat o cheltuială nedeductibilă ca deductibilă în D101?"
description: "Explică riscul de subevaluare a impozitului și controlul aplicat de iConta.eu pentru cel mai frecvent astfel de caz."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce faci dacă ai declarat o cheltuială nedeductibilă ca deductibilă în D101?

## Temeiul legal

::: ghid-temei
CF art.25 alin.(4) lit.a): cheltuiala cu impozitul pe profit (cont contabil 691) este nedeductibilă și trebuie adăugată înapoi la baza impozabilă.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.
:::

Tratarea unei cheltuieli nedeductibile ca deductibilă duce la subevaluarea impozitului pe profit declarat. Cel mai documentat astfel de caz, verificat la sursă, este chiar cheltuiala cu propriul impozit pe profit (cont 691) — nedeductibilă conform art.25 alin.(4) lit.a) și obligatoriu de adăugat înapoi la baza impozabilă.

## Ce se greșește în practică

Omisiunea acestei adăugări reduce artificial impozitul declarat, adesea fără să fie sesizată — pe un portofoliu testat, impactul măsurat a fost de 2.432 lei, fără niciun semnal anterior introducerii controlului dedicat.

## Ce face iConta.eu

iConta.eu emite un avertisment automat când soldul debitor al contului 691 (cheltuiala cu impozitul pe profit) e mai mare decât zero, iar rândul P23 (cheltuieli nedeductibile) e completat cu zero — semn tipic că impozitul pe profit propriu nu a fost adăugat înapoi ca nedeductibil (CF art.25 alin.(4) lit.a)). Măsurată pe un portofoliu de test, omiterea acestei adăugări a scăzut impozitul declarat cu 2.432 lei, fără niciun alt semnal înainte de introducerea acestui gard. iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`d101_struct_anaf.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
