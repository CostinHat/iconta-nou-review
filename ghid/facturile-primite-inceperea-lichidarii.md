---
title: "Ce fac cu facturile primite după începerea lichidării?"
description: "Facturile de achiziție primite pe parcursul procedurii de lichidare a unui SRL continuă să fie înregistrate contabil, până la finalizarea lichidării și radiere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac cu facturile primite după începerea lichidării?

Începerea procedurii de lichidare nu oprește existența contabilă și fiscală a firmei — societatea rămâne persoană juridică, cu obligația de a-și ține evidența, până la radierea efectivă din Registrul Comerțului, pe baza situațiilor financiare de lichidare.

## Temeiul legal

::: ghid-temei
„În termen de 5 zile de la terminarea lichidării, lichidatorii depun la registrul comerțului cererea de radiere a societății din registrul comerțului, pe baza raportului final de lichidare și a situațiilor financiare de lichidare prin care se prezintă situația patrimoniului, a creanțelor și repartizarea activelor rămase, după caz, inclusiv, dacă este cazul, dovada îndeplinirii obligației de calculare, reținere și plată a impozitului pe venit din lichidarea societății, prevăzută la art. 97 alin. (5) din Legea nr. 227/2015 privind Codul fiscal [...]"
— Legea 239/2025, art. VIII alin. (12) — notă la Legea 227/2015, art. 97 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta, în practică, pentru facturile primite în perioada de lichidare:

- Societatea rămâne obligată să țină evidența contabilă, inclusiv înregistrarea facturilor de achiziție primite, pe toată durata procedurii de lichidare — până la finalizarea acesteia și întocmirea situațiilor financiare de lichidare.
- Cheltuielile facturate în această perioadă (servicii de lichidator, taxe, utilități curente) intră în calculul rezultatului lichidării, alături de valorificarea activelor rămase.
- Radierea efectivă se face abia după depunerea raportului final de lichidare și a situațiilor financiare de lichidare la Registrul Comerțului, împreună cu dovada plății impozitului aferent câștigului din lichidare (art. 97 alin. 5).

## Ce se greșește în practică

- Se refuză înregistrarea facturilor primite după votul de dizolvare/începere a lichidării, considerând firma „deja închisă" — legal, firma continuă să existe și să aibă obligații fiscale până la radiere.
- Se ignoră TVA-ul deductibil pe facturile primite în perioada de lichidare, deși dreptul de deducere se păstrează atâta timp cât firma e încă înregistrată în scopuri de TVA.
- Se stabilește rezultatul lichidării înainte de a include toate facturile primite până la data situațiilor financiare de lichidare, ceea ce denaturează câștigul impozabil calculat la partaj.

## Ce face iConta.eu

Modulul de lichidare al iConta.eu (`core/lichidare.py`) generează notele contabile pentru valorificarea activelor și calculează partajul final (separând capitalul social neimpozabil de câștigul impozabil cu 10%, conform art. 97 alin. 5). Aplicația nu are un flux special care să blocheze sau să trateze diferit facturile de achiziție primite după începerea lichidării — acestea se introduc și se contabilizează prin modulul obișnuit de facturare (`core/contare_facturi.py`), la fel ca oricare altă factură primită de firmă, atâta timp cât societatea nu a fost încă radiată.

[iConta.eu](/)
