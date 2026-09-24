---
title: "Am uitat să adaug cheltuielile cu amenzile în nedeductibile"
description: "Explică onest ce confirmă dosarul despre nedeductibilitatea amenzilor și ce oferă aplicația ca mecanism general de control."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am uitat să adaug cheltuielile cu amenzile în nedeductibile

## Temeiul legal

::: ghid-temei
CF art.25 alin.(4) lit.b): „dobânzile/majorările de întârziere, amenzile, confiscările și penalitățile, datorate către autoritățile române/străine, potrivit prevederilor legale, cu excepția celor aferente contractelor încheiate cu aceste autorități" — nu sunt deductibile.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

CF art.25 alin.(4) lit.a): cheltuiala cu impozitul pe profit (cont contabil 691) este nedeductibilă și trebuie adăugată înapoi la baza impozabilă.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.
:::

Amenzile, majorările de întârziere, confiscările și penalitățile datorate autorităților (române sau străine) sunt nedeductibile conform art.25 alin.(4) lit.b), cu excepția celor aferente unor contracte încheiate cu acele autorități — și trebuie adăugate înapoi la baza impozabilă, la rândul P23 din D101. Cel mai documentat caz verificat la nivel de cod al aplicației este cel al cheltuielii cu propriul impozit pe profit, cont 691 (art.25 alin.(4) lit.a)), pentru care iConta.eu are un control automat dedicat (vezi mai jos) — pentru amenzi, principiul e același, dar sursele acestui dosar nu confirmă un control automat similar în aplicație.

## Ce se greșește în practică

Mecanismul general — omiterea unei cheltuieli nedeductibile din P23 — e ilustrat concret de cazul contului 691, unde omisiunea a scăzut impozitul declarat cu 2.432 lei pe un portofoliu testat, fără alt semnal.

## Ce face iConta.eu

iConta.eu emite un avertisment automat când soldul debitor al contului 691 (cheltuiala cu impozitul pe profit) e mai mare decât zero, iar rândul P23 (cheltuieli nedeductibile) e completat cu zero — semn tipic că impozitul pe profit propriu nu a fost adăugat înapoi ca nedeductibil (CF art.25 alin.(4) lit.a)). Măsurată pe un portofoliu de test, omiterea acestei adăugări a scăzut impozitul declarat cu 2.432 lei, fără niciun alt semnal înainte de introducerea acestui gard. iConta.eu are un avertisment dedicat pentru cazul specific al contului 691; pentru alte categorii de cheltuieli nedeductibile (inclusiv amenzi), sursele verificate nu confirmă un control automat similar — verificați manual rândul P23 înainte de generare. iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`opanaf_206_2025_d101.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
