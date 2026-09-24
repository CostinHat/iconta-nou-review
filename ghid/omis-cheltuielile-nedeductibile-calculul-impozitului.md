---
title: "Ce fac dacă am omis cheltuielile nedeductibile la calculul impozitului pe profit?"
description: "Explică rândul relevant din D101 și controlul aplicației pentru cel mai documentat caz de omisiune."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am omis cheltuielile nedeductibile la calculul impozitului pe profit?

## Temeiul legal

::: ghid-temei
CF art.25 alin.(4) lit.a): cheltuiala cu impozitul pe profit (cont contabil 691) este nedeductibilă și trebuie adăugată înapoi la baza impozabilă.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.
:::

Cheltuielile nedeductibile se raportează la rândul P23 din D101. Omiterea lor reduce artificial profitul impozabil și, implicit, impozitul declarat. Cel mai documentat exemplu verificat la sursă este cheltuiala cu propriul impozit pe profit (cont 691), nedeductibilă conform art.25 alin.(4) lit.a).

## Ce se greșește în practică

Omisiunea trece adesea neobservată dacă nu există un control dedicat — pe un portofoliu testat, impactul unei astfel de omisiuni a fost o subevaluare de 2.432 lei a impozitului declarat.

## Ce face iConta.eu

iConta.eu emite un avertisment automat când soldul debitor al contului 691 (cheltuiala cu impozitul pe profit) e mai mare decât zero, iar rândul P23 (cheltuieli nedeductibile) e completat cu zero — semn tipic că impozitul pe profit propriu nu a fost adăugat înapoi ca nedeductibil (CF art.25 alin.(4) lit.a)). Măsurată pe un portofoliu de test, omiterea acestei adăugări a scăzut impozitul declarat cu 2.432 lei, fără niciun alt semnal înainte de introducerea acestui gard. iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`opanaf_206_2025_d101.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
