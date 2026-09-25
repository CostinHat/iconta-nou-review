---
title: "Cum tratez pierderile din diferențe de curs la impozitul pe profit"
description: "Regula generală de la impozitul pe profit pentru cheltuielile din diferențe de curs valutar și de ce, în lipsa unei excluderi speciale, ele sunt deductibile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez pierderile din diferențe de curs la impozitul pe profit

Pierderile din diferențe de curs valutar (cheltuiala înregistrată în contul 665) urmează regula generală de calcul a rezultatului fiscal: pleci de la ce ai înregistrat contabil și scazi veniturile neimpozabile, adaugi cheltuielile nedeductibile. Legea nu prevede o excludere specială pentru diferențele de curs, deci ele rămân, ca regulă, cheltuieli deductibile la impozitul pe profit.

## Temeiul legal

::: ghid-temei
„(1) Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. La stabilirea rezultatului fiscal se iau în calcul și elemente similare veniturilor și cheltuielilor, potrivit normelor metodologice, precum și pierderile fiscale care se recuperează în conformitate cu prevederile art. 31. Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală."
— Legea 227/2015 (Codul fiscal), art. 19 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Punctul de plecare e cheltuiala din 665, așa cum a fost înregistrată contabil, conform OMFP 1802/2014 pct. 322 (decontare) sau pct. 325 (reevaluare lunară).
- Peste rezultatul contabil se aplică doar corecțiile explicit prevăzute de Codul fiscal: venituri neimpozabile (art. 23) și cheltuieli nedeductibile (art. 25). Niciunul dintre aceste articole nu tratează diferențele de curs valutar ca excepție de ordin general.
- Excepție punctuală: pentru costurile îndatorării (dobânzi și pierderi nete din diferențe de curs asociate finanțării), se aplică regulile speciale de limitare de la art. 40^2 (plafonare tip ATAD) — dar acestea vizează finanțarea, nu diferențele de curs din activitatea curentă (creanțe/datorii comerciale, disponibilități).
- Pentru firmele la impozit pe veniturile microîntreprinderilor regulile sunt altele — vezi ghidul dedicat „Diferențe de curs în calculul plafonului micro".

## Ce se greșește în practică

- Se presupune, fără temei, că pierderile din curs valutar ar fi nedeductibile parțial sau integral, prin analogie cu alte cheltuieli plafonate (ex. protocol, sponsorizări).
- Se aplică regula de limitare de la costurile îndatorării (art. 40^2) și la diferențele de curs din activitatea comercială curentă (facturi de marfă, servicii), deși aceasta vizează strict finanțarea prin datorii.
- Se omite corectarea rezultatului fiscal atunci când o eroare de calcul a diferenței de curs, descoperită ulterior, se corectează contabil pe rezultatul reportat — caz în care se depune declarație rectificativă, nu se ajustează doar perioada curentă.

## Ce face iConta.eu

`core/diferente_curs.py` este un motor contabil pur: calculează diferența (câștig sau pierdere) și generează nota pe 665/765, la decontare sau la reevaluarea lunară. Aplicația **nu calculează impozitul pe profit** și nu aplică regulile de la art. 19-40^2 asupra acestor sume — nu există nicio legătură de cod între modulul de diferențe de curs și motorul declarației de impozit pe profit. Tratamentul fiscal descris mai sus se aplică manual, pe baza rulajului conturilor 665/765 din balanța generată de iConta.eu, nu automat, în aplicație.

[iConta.eu](/)
