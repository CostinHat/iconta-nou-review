---
title: "Veniturile din diferențe de curs valutar: impozabile"
description: "Confirmare: veniturile din diferențe de curs valutar (cont 765) sunt, ca regulă, impozabile integral la impozitul pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Veniturile din diferențe de curs valutar: impozabile

Da, veniturile din diferențe de curs valutar (cont 765) sunt impozabile la impozitul pe profit, la fel ca orice alt venit financiar înregistrat contabil. Codul fiscal nu le include în lista veniturilor neimpozabile aplicabilă firmelor obișnuite, deci ele măresc rezultatul fiscal exact cum au fost înregistrate.

## Temeiul legal

::: ghid-temei
„(1) Rezultatul fiscal se calculează ca diferență între veniturile și cheltuielile înregistrate conform reglementărilor contabile aplicabile, din care se scad veniturile neimpozabile și deducerile fiscale și la care se adaugă cheltuielile nedeductibile. [...] Rezultatul fiscal pozitiv este profit impozabil, iar rezultatul fiscal negativ este pierdere fiscală."
— Legea 227/2015 (Codul fiscal), art. 19 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula de bază: veniturile din 765 intră în calculul rezultatului fiscal, la fel ca orice alt venit înregistrat conform reglementărilor contabile — nu apar pe lista veniturilor neimpozabile aplicabilă societăților comerciale obișnuite (art. 23 Cod fiscal).
- Excepție de reținut: pentru **organizații nonprofit, sindicale și patronale**, „veniturile din dividende, dobânzi, precum și din diferențele de curs valutar aferente disponibilităților și veniturilor neimpozabile" sunt neimpozabile — dar acesta e un regim distinct, aplicabil doar acelor entități, nu societăților comerciale plătitoare de impozit pe profit.
- La **microîntreprinderi**, veniturile din 765 nu se impozitează în baza lunară/trimestrială (se scad, art. 53 alin. (1) lit. h), dar sunt regularizate, ca diferență favorabilă netă, în trimestrul IV (art. 53 alin. (2) lit. b) — deci tot ajung, până la urmă, în calculul impozitului micro.
- Pentru instituțiile de credit, există o excepție punctuală (art. 15 alin. (1)) pentru rezervele de influențe de curs valutar aferente aprecierii disponibilităților în valută — irelevantă pentru firmele obișnuite.

## Ce se greșește în practică

- Se aplică regula de neimpozitare specifică organizațiilor nonprofit (art. 15 alin. (2) lit. f) și la societăți comerciale obișnuite, care nu se încadrează în acel regim.
- Se presupune că veniturile din diferențe de curs ar avea, ca regulă generală, un tratament preferențial similar dividendelor primite (neimpozabile) — nu au; regimul lor e cel obișnuit de venit financiar.
- La microîntreprinderi, se ignoră regularizarea din trimestrul IV, tratând veniturile din 765 ca fiind permanent neimpozitate, nu doar amânate.

## Ce face iConta.eu

Motorul `core/diferente_curs.py` generează corect venitul din 765 la fiecare câștig de curs valutar, fie la decontare, fie la reevaluarea lunară. Aplicația **nu calculează impozitul pe profit** și nu decide dacă acel venit e sau nu impozabil — nu există în cod nicio verificare a regimului fiscal al firmei (societate comercială obișnuită, organizație nonprofit sau instituție de credit) care să aplice vreuna dintre excepțiile de mai sus. Contabilul preia venitul din balanța generată de iConta.eu și îl încadrează fiscal, corect, în funcție de tipul entității și de regimul ei de impozitare.

[iConta.eu](/)
