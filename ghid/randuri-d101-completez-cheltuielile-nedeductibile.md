---
title: "Ce rânduri din D101 completez pentru cheltuielile nedeductibile"
description: "Precizează rândurile D101 confirmate în dosar pentru cheltuielile nedeductibile."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce rânduri din D101 completez pentru cheltuielile nedeductibile

## Temeiul legal

::: ghid-temei
CF art.25 alin.(4) lit.a): cheltuiala cu impozitul pe profit (cont contabil 691) este nedeductibilă și trebuie adăugată înapoi la baza impozabilă.
— Legea 227/2015 (Codul fiscal) consolidată, `anaf_surse/cod_fiscal_227_2015_consolidat.txt` + `core/d101.py`, dosar de cercetare F027.
:::

Rândul principal pentru cheltuielile nedeductibile este P23 din D101 — total cheltuieli nedeductibile, verificat de aplicație în avertismentul dedicat contului 691. Pentru cheltuiala cu amortizarea contabilă tratată ca nedeductibilă, sursele verificate arată că valoarea intră în rollup-ul P34 „cheltuieli nedeductibile”, prin rândurile de tip P2x/P28.

## Ce se greșește în practică

Se greșește prin confundarea P11 (amortizarea fiscală, o deducere) cu P2x/P28/P34 (amortizarea contabilă, un add-back) — sunt rânduri cu roluri opuse.

## Ce face iConta.eu

D101 tratează amortizarea ca intrare, nu o calculează: P11 este amortizarea fiscală (deducere — intră în P16, total deduceri, și reduce profitul impozabil), iar rândurile de tip P2x/P28 reprezintă cheltuiala cu amortizarea contabilă, care intră în rollup-ul P34 „cheltuieli nedeductibile” și se adaugă înapoi la baza impozabilă. Contabilul introduce manual ambele valori în iConta.eu. iConta.eu emite un avertisment automat când soldul debitor al contului 691 (cheltuiala cu impozitul pe profit) e mai mare decât zero, iar rândul P23 (cheltuieli nedeductibile) e completat cu zero — semn tipic că impozitul pe profit propriu nu a fost adăugat înapoi ca nedeductibil (CF art.25 alin.(4) lit.a)). Măsurată pe un portofoliu de test, omiterea acestei adăugări a scăzut impozitul declarat cu 2.432 lei, fără niciun alt semnal înainte de introducerea acestui gard.

[iConta.eu](/)
