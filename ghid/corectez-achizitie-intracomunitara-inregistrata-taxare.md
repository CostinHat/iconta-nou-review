---
title: "Cum corectez o achiziție intracomunitară înregistrată fără taxare inversă?"
description: O achiziție intracomunitară de bunuri se corectează cu formula generală de autolichidare (4426=4427), pe rândurile D300 dedicate achizițiilor intracomunitare — nu pe cele ale taxării inverse interne, art. 331.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez o achiziție intracomunitară înregistrată fără taxare inversă?

Mai întâi, precizarea de temei: o achiziție intracomunitară de bunuri nu se supune art. 331 (taxarea inversă internă, limitată prin lege la operațiuni în interiorul României), ci art. 308 din Codul fiscal. Colocvial, ambele mecanisme sunt numite „taxare inversă" de mulți contabili, dar au articole și, în aplicație, rânduri de declarație diferite.

## Temeiul legal

::: ghid-temei
„Persoana care efectuează o achiziție intracomunitară de bunuri care este taxabilă, conform prezentului titlu, este obligată la plata taxei."
— Legea 227/2015, art. 308 alin. (1)
:::

::: ghid-temei
„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă."
— HG 1/2016, pct. 109 alin. (1)
:::

Corecția, în linii mari:
1. Identifică perioada în care ar fi trebuit înregistrată autolichidarea și verifică dacă achiziția a fost înregistrată doar ca marfă/cheltuială, fără nota de autolichidare.
2. Înregistrează nota lipsă: `4426 = 4427`, la valoarea taxei aferente achiziției (cota aplicabilă la valoarea în lei a bunurilor).
3. Reflectă corect suma în decont — pentru achiziții intracomunitare de **bunuri**, rândurile dedicate din D300 sunt distincte de cele folosite pentru taxarea inversă internă (art. 331): nu se introduc pe aceleași rânduri de decont, ci pe cele specifice achizițiilor intracomunitare.
4. Verifică dreptul de deducere al taxei autolichidate — se aplică în limitele și condițiile obișnuite de deducere (art. 297-301 din Codul fiscal).

**Notă**: motorul de taxare inversă verificat pentru acest ghid (`core/taxare_inversa.py`) acoperă exclusiv categoriile din art. 331 (operațiuni interne) — el nu e sursa de comportament pentru achizițiile intracomunitare de bunuri. Codul specific acestora, din modulul dedicat operațiunilor intracomunitare, nu a fost examinat linie cu linie pentru acest ghid; dacă ai nevoie de detalii tehnice suplimentare despre exact cum se completează rândurile respective în aplicație, verifică direct ecranul de operațiuni intracomunitare.

## Ce se greșește în practică

- Se corectează achiziția prin ecranul/categoriile de taxare inversă internă (art. 331), deși achizițiile intracomunitare de bunuri au un temei și, în declarație, rânduri distincte.
- Se înregistrează doar factura de achiziție, fără nota de autolichidare `4426=4427`, lăsând taxa neînregistrată complet.
- Se corectează contabilitatea, dar se omite rectificarea decontului de TVA din perioada în care eroarea a apărut inițial.

## Ce face iConta.eu

Motorul de taxare inversă internă din iConta.eu (categoriile de la art. 331) nu acoperă achizițiile intracomunitare de bunuri — pentru acestea, folosește ecranul dedicat operațiunilor intracomunitare, care alimentează rândurile specifice din D300, distincte de cele ale taxării inverse interne. Acest modul nu a fost verificat în detaliu, la nivel de cod, pentru acest ghid — dacă corecția implică o perioadă deja declarată, verifică direct în aplicație procedura de rectificare a decontului aferent acelei perioade.

[iConta.eu](/)
