---
title: Plățile anticipate de impozit pe profit 2026: care sunt regulile?
description: În 2026 coexistă două regimuri de impozit pe profit — declarare trimestrială standard (D100, trimestrele I-III, bază cumulată) și declarare anuală cu plăți anticipate opționale (1/4 din impozitul anului precedent, trimestrul IV cu termen 25 decembrie).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Plățile anticipate de impozit pe profit 2026: care sunt regulile?

Termenul „plăți anticipate" e folosit uneori impropriu pentru orice plată trimestrială de impozit pe profit, dar Codul fiscal definește de fapt două regimuri distincte, cu formule de calcul complet diferite. Separarea corectă a celor două e esențială pentru 2026.

## Temeiul legal

::: ghid-temei
**CF art. 41 alin. (1):**
> „Calculul, declararea și plata impozitului pe profit, cu excepțiile prevăzute de prezentul articol, se
> efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III.
> Definitivarea și plata impozitului pe profit aferent anului fiscal respectiv se efectuează până la
> termenul de depunere a declarației privind impozitul pe profit prevăzut la art. 42."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:4532-4534`

**CF art. 41 alin. (2)-(3):**
> „Contribuabilii, alții decât cei prevăzuți la alin. (4) și (5), pot opta pentru calculul, declararea și
> plata impozitului pe profit anual, cu plăți anticipate, efectuate trimestrial... Opțiunea este
> obligatorie pentru cel puțin 2 ani fiscali consecutivi."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:4536-4544`

**CF art. 41 alin. (8):**
> „Contribuabilii care aplică sistemul de declarare și plată a impozitului pe profit anual, cu plăți
> anticipate efectuate trimestrial, determină plățile anticipate trimestriale în sumă de o pătrime din
> impozitul pe profit datorat pentru anul precedent, actualizat cu indicele prețurilor de consum...
> cu excepția plății anticipate aferente trimestrului IV care se declară și se plătește până la data
> de 25 decembrie, respectiv până la data de 25 a ultimei luni din anul fiscal modificat."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:4600-4602`

**OPANAF 587/2016, Anexa 4, Cap. I, pct. 1.3 lit. a):**
> „până la data de 25 decembrie, pentru plățile anticipate aferente trimestrului IV, în cazul
> contribuabililor care declară și plătesc impozit pe profit anual, cu plăți anticipate efectuate
> trimestrial, și care determină plățile anticipate trimestriale în sumă de o pătrime din impozitul
> datorat pentru anul precedent, potrivit art. 41 alin. (8)..."
— sursă: `anaf_surse/opanaf_587_2016_aprobarea_modelului_continutului_formularelor_utilizate.txt:987-990`
:::

## Cele două regimuri, puse față în față

**Regimul standard** (art. 41 alin. 1, aplicat implicit dacă nu s-a optat pentru celălalt): declarare trimestrială D100 pentru trimestrele I-III, cu bază egală cu profitul efectiv cumulat de la 1 ianuarie, urmată de definitivare și regularizare anuală prin declarația D101.

**Regimul opțional cu plăți anticipate** (art. 41 alin. 2-3 și 8): declarare și plată anuală, dar cu plăți anticipate trimestriale calculate ca 1/4 din impozitul datorat pentru anul precedent, actualizat cu indicele prețurilor de consum — nu pe baza profitului efectiv al anului curent. Excepție: plata anticipată a trimestrului IV se declară și se plătește până la 25 decembrie, nu la termenul general. Odată aleasă, opțiunea e obligatorie minimum 2 ani fiscali consecutivi.

Cele două regimuri nu se amestecă: un contribuabil pe regim standard nu calculează 1/4 din anul precedent, iar unul pe regim opțional nu calculează pe profitul cumulat efectiv al trimestrului curent.

## Ce se greșește în practică

- Se presupune că toate firmele plătitoare de impozit pe profit sunt automat pe regimul cu „plăți anticipate" — regimul implicit e cel standard (bază cumulată), plățile anticipate fiind o opțiune separată.
- Se aplică formula 1/4 din anul precedent fără ca opțiunea să fi fost comunicată/exercitată oficial.
- Se schimbă regimul ales înainte de expirarea perioadei minime de 2 ani fiscali consecutivi.
- Se declară trimestrul IV la termenul general (25 a lunii următoare) în regimul opțional, deși legea fixează 25 decembrie pentru acest regim.

## Ce face iConta.eu

Vectorul fiscal al firmei (`core/vector_fiscal_api.py`) reține doar regimurile „micro" și „profit" — nu are un atribut care să marcheze opțiunea pentru regimul anual cu plăți anticipate trimestriale (art. 41 alin. 2-3). Ca urmare, `core/d100.py` calculează întotdeauna, pentru o firmă pe „profit", formula regimului standard — bază cumulată de la 1 ianuarie — indiferent dacă firma a optat sau nu pentru regimul cu plăți anticipate. Dacă firma dvs. a exercitat această opțiune, formula de 1/4 din impozitul anului precedent nu este calculată automat de aplicație și trebuie determinată separat.

Notă suplimentară: modulul de scadențar folosit de semaforul de obligații (`core/scadente.py`) nu are o ramură dedicată pentru tipul „d100" și, pentru trimestrul IV, cade pe regula generică (25 ianuarie anul următor) — diferită atât de 25 decembrie (cod 103, regim standard cu formula cumulată aplicată la trimestrul IV), cât și de scadența specifică a regimului opțional. Pentru orice termen din trimestrul IV, verificați data din declarația efectiv generată, nu doar afișajul din semafor.

[iConta.eu](/)
