---
title: "Firmă pe profit scutită de TVA: cum declar impozitul"
description: "Regimul de declarare a impozitului pe profit pentru firmele care desfășoară operațiuni scutite de TVA fără drept de deducere, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Firmă pe profit scutită de TVA: cum declar impozitul

O firmă poate desfășura o activitate scutită de TVA fără drept de deducere (servicii medicale, educaționale, sociale etc.) și, în același timp, să fie plătitoare de impozit pe profit. Cele două regimuri — TVA și impozit pe profit — sunt complet independente.

## Temeiul legal

::: ghid-temei
„Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III. Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— Legea 227/2015 (Codul fiscal), art. 41 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta pentru o firmă scutită de TVA conform art. 292 (spitalizare, îngrijiri medicale, învățământ, asistență socială și altele asemenea, enumerate expres la acel articol):

- Scutirea de TVA fără drept de deducere (art. 292) este o categorie separată de scutirea pentru întreprinderi mici (art. 310) — o firmă poate fi scutită prin natura operațiunilor, indiferent de cifra de afaceri, și poate desfășura o activitate perfect obișnuită la impozitul pe profit.
- **Nu există niciun regim special de declarare a impozitului pe profit** pentru firmele scutite de TVA — se aplică exact regulile generale de la art. 41-42: declarare trimestrială cu plată până pe 25 ale lunii următoare (sau opțional anuală, cu plăți anticipate trimestriale), și definitivare prin declarația anuală privind impozitul pe profit (D101).
- Faptul că firma nu colectează și nu deduce TVA nu modifică baza de calcul a impozitului pe profit — profitul impozabil se determină după regulile obișnuite (venituri minus cheltuieli deductibile, cu ajustările prevăzute de titlul II din Codul fiscal), indiferent de statutul de TVA.
- Singura legătură indirectă: TVA nedeductibilă (pentru că nu există drept de deducere) devine, de regulă, parte din costul de achiziție al bunurilor/serviciilor, influențând astfel cheltuielile deductibile la impozitul pe profit — dar acesta e un efect al contabilizării TVA, nu o regulă specială de declarare a impozitului.

## Ce se greșește în practică

- Se presupune, greșit, că o firmă scutită de TVA are și un regim simplificat sau diferit de declarare a impozitului pe profit.
- Se omite depunerea declarațiilor trimestriale/anuale de impozit pe profit, considerând că „firma e scutită", confundând scutirea de TVA cu o scutire generală de obligații fiscale.
- Se calculează greșit baza impozabilă, uitând să se includă în costuri TVA nedeductibilă aferentă achizițiilor legate de activitatea scutită.

## Ce face iConta.eu

Am verificat în `core/d101.py`: modulul de impozit pe profit **nu condiționează în niciun fel calculul sau declararea de statutul de plătitor de TVA al firmei** — regulile de declarare trimestrială/anuală se aplică identic, indiferent dacă firma este sau nu înregistrată în scopuri de TVA. Aplicația generează declarația D101 conform regulilor generale de la art. 41-42 din Codul fiscal; corecta încadrare a operațiunilor ca scutite conform art. 292 și impactul asupra TVA nedeductibile rămân în sarcina contabilului.

[iConta.eu](/)
