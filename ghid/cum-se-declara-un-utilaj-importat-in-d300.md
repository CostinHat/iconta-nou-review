---
title: Cum se declară un utilaj importat în D300?
description: Un utilaj importat nu e vehicul rutier motorizat, deci nu intră sub limitarea de 50% a dreptului de deducere — dar rândul din D300 (rd.7 sau rd.24, după regimul vamal) trebuie introdus manual, aplicația nu îl derivă automat din factură.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se declară un utilaj importat în D300?

Un utilaj sau echipament importat nu are aceleași reguli de deducere ca un vehicul rutier motorizat, dar declararea lui în D300 depinde de regimul vamal aplicat la import și trebuie introdusă manual — aplicația nu citește automat un flag „import” de pe factură.

## Temeiul legal

::: ghid-temei
„(1) Dreptul de deducere ia naștere la momentul exigibilității taxei.”
— art.297 alin.(1) Cod fiscal

„(1) Prin excepție de la prevederile art. 297 se limitează la 50% dreptul de deducere a taxei
aferente cumpărării, achiziției intracomunitare, importului, închirierii sau leasingului de
vehicule rutiere motorizate și a taxei aferente cheltuielilor legate de vehiculele aflate în
proprietatea sau în folosința persoanei impozabile, în cazul în care vehiculele nu sunt
utilizate exclusiv în scopul activității economice.
(2) Restricția prevăzută la alin. (1) nu se aplică vehiculelor rutiere motorizate având o
masă totală maximă autorizată care depășește 3.500 kg sau mai mult de 9 scaune [...]”
— art.298 alin.(1)-(2) Cod fiscal
:::

## De ce un utilaj nu intră sub limitarea de 50%

Limitarea de 50% de la art.298 se aplică explicit doar „vehiculelor rutiere motorizate” — cumpărare, achiziție intracomunitară, import, închiriere sau leasing — atunci când acestea nu sunt folosite exclusiv în scop economic. Un utilaj sau echipament importat (o linie de producție, un utilaj industrial) nu e un vehicul rutier motorizat, așa că nu intră sub această restricție, indiferent de utilizarea lui.

Rândul din decont unde se declară TVA la import depinde de regimul vamal folosit efectiv:
- dacă furnizorul aplică regimul de taxare inversă la import prevăzut pentru anumite situații (cont special de TVA), operațiunea se declară la rândul dedicat taxării inverse la import;
- dacă TVA a fost plătit efectiv în vamă (nu prin cont special), suma se declară la rândul de achiziții deductibile pe cota corespunzătoare, alături de celelalte achiziții din jurnalul de cumpărări.

## Ce se greșește în practică

- Se aplică din reflex limitarea de 50% și la utilaje sau echipamente, deși restricția vizează strict vehiculele rutiere motorizate.
- Se introduce TVA-ul la import direct ca deducere obișnuită, fără să se verifice ce regim vamal a fost folosit (cont special vs. plată efectivă în vamă).
- Se lipsesc documentele vamale (declarația vamală de import) care justifică suma introdusă manual.
- Se așteaptă ca aplicația să detecteze automat, din factura de achiziție, că e vorba de un import supus taxării inverse — acest lucru nu se întâmplă automat.

## Ce face iConta.eu

`calcul_d300` preia integral TVA din antetul și liniile facturii, fără nicio verificare a tipului de bun (vehicul vs. utilaj) sau a utilizării exclusiv economice — nu există un gard automat pentru limitarea de 50%, tocmai pentru că ea nu se aplică decât vehiculelor. Rândul pentru achiziții cu taxare inversă la import e complet manual — codul nu citește un flag „import” de pe factură pentru a-l deriva automat; baza de impozitare și TVA-ul trebuie introduse manual la rândul corect, în funcție de regimul vamal aplicat efectiv.

[iConta.eu](/)
