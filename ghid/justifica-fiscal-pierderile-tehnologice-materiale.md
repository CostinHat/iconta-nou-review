---
title: "Cum se justifică fiscal pierderile tehnologice de materiale pe șantier?"
description: "Explică distincția legală dintre pierderile tehnologice și perisabilități, și de ce norma de consum propriu, nu HG 831/2004, e temeiul corect pe șantier."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se justifică fiscal pierderile tehnologice de materiale pe șantier?

Materialele consumate/pierdute în procesul de construcție nu intră, din punct de vedere fiscal, sub aceeași categorie ca perisabilitățile mărfurilor din comerț — legea le tratează separat, cu un temei și o justificare diferite.

## Temeiul legal

::: ghid-temei
"Următoarele cheltuieli au deductibilitate limitată: [...] d) scăzămintele, perisabilitățile, pierderile rezultate din manipulare/depozitare, potrivit legii; e) pierderile tehnologice care sunt cuprinse în norma de consum proprie necesară pentru fabricarea unui produs sau prestarea unui serviciu;"
— Codul fiscal (Legea 227/2015), art. 25 alin. (3) lit. d)-e), `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, dosar de cercetare F066.
:::

Legea distinge explicit între cele două categorii: scăzămintele/perisabilitățile (lit. d) se justifică "potrivit legii" — adică prin coeficienții stabiliți în HG 831/2004, aplicabili mărfurilor în procesul de comercializare. Pierderile tehnologice (lit. e) se justifică prin "norma de consum proprie" — un standard intern, stabilit și documentat de firmă însăși pentru procesul ei de fabricare sau prestare de servicii, nu printr-un procent fixat de un act normativ. Materialele pierdute/consumate pe un șantier (tăieri, resturi, manipulare în procesul de construcție) sunt, conceptual, mai aproape de pierderi tehnologice (lit. e) — un proces de prestare/producție — decât de perisabilitatea mărfurilor de vânzare (lit. d).

## Ce se greșește în practică

Greșeala frecventă e aplicarea directă a unui procent din HG 831/2004 (gândit pentru mărfuri comercializate ca atare) la pierderile de materiale de construcție consumate în procesul de execuție. HG 831/2004 vizează explicit "mărfuri în procesul de comercializare", nu materiale de construcție consumate tehnologic. A doua greșeală e lipsa unei norme de consum proprii documentate (deviz, fișă tehnologică, standard intern), fără de care pierderea nu are, de fapt, o bază de justificare la control.

## Ce face iConta.eu

Motorul de perisabilități al iConta.eu (`core/perisabilitati.py`) e construit strict pentru HG 831/2004 și exclude explicit acest caz din docstring-ul propriu: "NU sunt perisabilitati: consum tehnologic, neglijenta, sustrageri, forta majora." iConta.eu nu are un modul dedicat calculului sau limitării unei norme de consum propriu pentru pierderi tehnologice — verificat direct în codul de producție (`core/productie.py`) și de rețete (`core/retete.py`), fără nicio logică de acest tip. Justificarea unei pierderi tehnologice pe șantier rămâne, așadar, un act de documentare profesională a firmei (deviz de execuție, fișă tehnologică, normă internă de consum), nu un calcul automatizat în aplicație.

[iConta.eu](/)
