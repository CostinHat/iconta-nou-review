---
title: "Cum influențează amortizarea baza impozabilă la profit"
description: "Mecanismul prin care cheltuiala cu amortizarea unui mijloc fix se recuperează fiscal treptat, conform Codului fiscal, și reduce rezultatul fiscal impozabil în fiecare perioadă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum influențează amortizarea baza impozabilă la profit

Un mijloc fix nu devine cheltuială deductibilă dintr-o dată, la cumpărare, ci treptat, pe durata lui normală de funcționare. Amortizarea fiscală e mecanismul prin care costul unui utilaj, al unei clădiri sau al unui echipament „intră" în calculul impozitului pe profit, an de an, în locul unei singure cheltuieli uriașe la achiziție.

## Temeiul legal

::: ghid-temei
„(1) Cheltuielile aferente achiziționării, producerii, construirii mijloacelor fixe amortizabile, precum și investițiile efectuate la acestea se recuperează din punct de vedere fiscal prin deducerea amortizării potrivit prevederilor prezentului articol.
(2) Mijlocul fix amortizabil este orice imobilizare corporală care îndeplinește cumulativ următoarele condiții: a) este deținut și utilizat în producția, livrarea de bunuri sau în prestarea de servicii, pentru a fi închiriat terților sau în scopuri administrative; [...] c) are o durată normală de utilizare mai mare de un an."
— Legea nr. 227/2015 (Codul fiscal), art. 28 alin. (1), (2) lit. a), c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta pentru baza impozabilă:

- Prețul de achiziție al unui mijloc fix **nu e deductibil integral în anul cumpărării** — el se recuperează fiscal treptat, prin amortizare, pe durata normală de utilizare stabilită conform catalogului aprobat prin HG 2.139/2004.
- Fiecare rată lunară/anuală de amortizare fiscală reduce rezultatul fiscal (baza de calcul a impozitului pe profit) în perioada respectivă — cu cât durata de amortizare e mai lungă, cu atât efectul asupra impozitului e mai întins în timp.
- Nu orice imobilizare corporală e mijloc fix amortizabil în sens fiscal: trebuie îndeplinite cumulativ condițiile de la alin. (2) — utilizare în activitatea economică, prag valoric minim (actualizat periodic) și durată de utilizare de peste un an. Un bun sub prag sau cu durată sub un an se deduce integral ca și cheltuială curentă, nu prin amortizare.
- Amortizarea contabilă (calculată după reglementările contabile) și amortizarea fiscală (calculată după regulile Codului fiscal) pot diferi — la calculul rezultatului fiscal contează amortizarea fiscală, nu neapărat cea înregistrată în contabilitate.

## Ce se greșește în practică

- Se deduce integral, ca și cheltuială curentă, costul unui mijloc fix care depășește pragul valoric și durata de un an, în loc să fie amortizat treptat.
- Se presupune că amortizarea contabilă (metoda și durata aleasă în contabilitate) e automat identică cu cea fiscală, fără să se verifice dacă durata folosită se încadrează în limitele din catalogul HG 2.139/2004.
- Nu se face distincția între investițiile care majorează valoarea unui mijloc fix existent (amortizabile separat sau prin majorarea valorii) și cheltuielile de întreținere curentă, care sunt deductibile integral, imediat.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează amortizarea mijloacelor fixe pe baza datelor introduse de utilizator — categorie, valoare de intrare, durată normală de utilizare, metodă — folosind modulele `core/mijloace_fixe_import_api.py` și `core/repo_mijloace_fixe.py`, cu reflectare directă în registrul de amortizare și în calculul impozitului pe profit din D101 (`core/d101.py`). Aplicația nu decide însă categoria de mijloc fix sau durata normală de utilizare aplicabilă unui bun anume din catalogul HG 2.139/2004 — aceste încadrări rămân o decizie a contabilului la introducerea mijlocului fix în aplicație.

[iConta.eu](/)
