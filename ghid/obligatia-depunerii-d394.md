---
title: "Cine are obligația depunerii D394?"
description: "Persoanele impozabile care trebuie să depună declarația informativă 394 privind livrările, prestările și achizițiile efectuate pe teritoriul național."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cine are obligația depunerii D394?

Declarația 394 nu se depune de toți plătitorii de TVA pentru toate operațiunile — obligația e legată strict de operațiunile realizate pe teritoriul național de persoane înregistrate în scopuri de TVA. Confuzia cu D390 (operațiuni intracomunitare) este frecventă.

## Temeiul legal

::: ghid-temei
„Declarația se completează şi se depune de către: a) persoanele impozabile înregistrate în scopuri de TVA în România conform art. 316 din Legea nr. 227/2015 privind Codul fiscal [...] şi care sunt obligate la plata taxei conform art. 307 alin. (1), (2), (6) şi (7) din Codul fiscal, pentru operaţiuni impozabile în România conform art. 268 alin. (1) şi taxabile cu cota prevăzută de Codul fiscal. [...] b) persoanele impozabile înregistrate în scopuri de TVA în România conform art. 316 din Codul fiscal, care realizează în România achiziţii de bunuri sau servicii."
— OPANAF nr. 3.769/2015, Anexa nr. 2, pct. 1 lit. a) și b) (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt)
:::

În practică, obligația de depunere revine:

- Oricărei **persoane impozabile înregistrate în scopuri de TVA în România** (conform art. 316 Cod fiscal), pentru **livrările/prestările** pentru care a emis factură pe teritoriul național, inclusiv avansuri și operațiuni cu TVA la încasare.
- Aceleiași categorii de persoane, pentru **achizițiile** de bunuri sau servicii realizate în România, inclusiv facturile primite cu mențiunea „taxare inversă” sau „TVA la încasare”.
- Declarația se depune chiar dacă într-o perioadă de raportare firma nu a avut operațiuni — se bifează „NU” la secțiunea corespunzătoare, nu se omite depunerea.

## Ce se greșește în practică

- Se confundă D394 (operațiuni naționale) cu D390 (operațiuni intracomunitare) și se raportează în declarația greșită livrări/achiziții din UE.
- Se omite depunerea D394 în lunile fără activitate, considerându-se că declarația e necesară doar când există tranzacții de raportat.
- Nu se raportează separat bonurile fiscale și facturile simplificate care îndeplinesc condițiile unei facturi simplificate, deși OPANAF 3.769/2015 le cere înscrise distinct.

## Ce face iConta.eu

iConta.eu emite facturi și evidențiază achizițiile firmei, iar din modulul dedicat generează și structura D394 pe baza documentelor introduse în aplicație (fișierul `core/d394.py` din motorul aplicației). Corectitudinea încadrării fiecărei operațiuni (cotă, tip document, partener) rămâne responsabilitatea contabilului care validează declarația înainte de depunere.

[iConta.eu](/)
