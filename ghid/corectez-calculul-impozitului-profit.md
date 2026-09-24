---
title: "Cum corectez calculul impozitului pe profit?"
description: "Trece în revistă, pe baza dosarului, principalele cauze de calcul greșit al impozitului pe profit și limita curentă de corectare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez calculul impozitului pe profit?

## Temeiul legal

::: ghid-temei
Art.17 CF: "Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%."
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F027.

CF art.25 alin.(4) lit.a): cheltuiala cu impozitul pe profit (cont contabil 691) este nedeductibilă și trebuie adăugată înapoi la baza impozabilă.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.
:::

Impozitul pe profit se calculează la cota de 16% (art.17) pe profitul impozabil (P40 → P411), după aplicarea deducerilor (P11 amortizare fiscală, P13 rezervă legală) și a add-back-urilor pentru cheltuieli nedeductibile (P23/P34, inclusiv cheltuiala cu propriul impozit pe profit, cont 691, conform art.25 alin.(4) lit.a)). Un calcul greșit provine, cel mai frecvent, din omiterea unuia dintre aceste rânduri sau, pentru firmele mari, din impozitul minim pe cifra de afaceri (IMCA).

## Ce se greșește în practică

Cauze frecvente: omiterea add-back-ului pentru cont 691 (subevaluare), omiterea deducerii fiscale P11 (supraevaluare), sau — pentru anul fiscal 2026, la firmele eligibile IMCA — bug-ul de cotă descris mai jos.

## Ce face iConta.eu

iConta.eu emite un avertisment automat când soldul debitor al contului 691 (cheltuiala cu impozitul pe profit) e mai mare decât zero, iar rândul P23 (cheltuieli nedeductibile) e completat cu zero — semn tipic că impozitul pe profit propriu nu a fost adăugat înapoi ca nedeductibil (CF art.25 alin.(4) lit.a)). Măsurată pe un portofoliu de test, omiterea acestei adăugări a scăzut impozitul declarat cu 2.432 lei, fără niciun alt semnal înainte de introducerea acestui gard. Atenție: motorul D101 din iConta.eu calculează astăzi IMCA cu formula `impozit_minim_cifra_afaceri`, cablată pe cota fixă de 1% (`core/d101.py`, confirmat de testul `test_imca_formula_1pct_din_vt_vs_i_a`), deși legea prevede explicit 0,5% pentru anul fiscal 2026 (art.18^1 alin.(16) CF, introdus prin OUG 89/2025). Dacă firma dvs. se încadrează la IMCA pentru 2026, impozitul minim generat de aplicație poate fi dublu față de cel legal — verificați manual suma până la corectarea acestui bug. iConta.eu nu generează în prezent o D101 rectificativă din interfață: toate flagurile de stare din structura XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt fixate la `"0"` direct în cod (`build_xml`, `core/d101.py`), fără niciun parametru de intrare care să le poată seta. Modulul de rectificative din aplicație (D710) acoperă doar obligațiile declarate prin D100 (cod 121 micro / cod 103 profit trimestrial), nu și D101. Corectarea unei D101 deja depuse trebuie făcută astăzi direct la ANAF, în afara aplicației; nici sursele legale locale nu conțin un act normativ dedicat procedurii de rectificare a D101 (spre deosebire de D710, unde OPANAF 649/2025 e citat explicit), deși structura XML oficială (`opanaf_206_2025_d101.txt`) confirmă existența flagului `d_rec` la nivel de formular.

[iConta.eu](/)
