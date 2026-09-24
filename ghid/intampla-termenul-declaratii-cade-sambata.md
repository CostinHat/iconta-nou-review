---
title: Ce se întâmplă dacă termenul unei declarații cade sâmbăta sau duminica?
description: Termenul se mută automat pe următoarea zi lucrătoare — regulă confirmată ca fiind implementată în aplicație, ținând cont atât de weekend, cât și de sărbătorile legale (fixe și mobile). Vezi mecanismul și un exemplu concret pentru 2026.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce se întâmplă dacă termenul unei declarații cade sâmbăta sau duminica?

Când data nominală a unei declarații (de regulă ziua 25 a lunii următoare) cade sâmbătă sau duminică, termenul nu rămâne în weekend — se mută pe următoarea zi lucrătoare. Aceeași mutare se aplică și atunci când data nominală cade într-o zi de sărbătoare legală.

## Temeiul legal

::: ghid-temei
„...sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate." — Codul fiscal, art.147 alin.(1) (exemplu de termen „ziua 25", tipar valabil pentru majoritatea declarațiilor)
:::

**De semnalat onest**: calendarul de sărbători legale folosit pentru mutarea termenelor are ca bază declarată art.139 din Codul muncii, care enumeră atât zilele fixe, cât și cele cinci zile mobile (calculate după Paștele ortodox, valabile pentru intervalul 2024–2099). Regula generică de „prorogare pentru prima zi lucrătoare" e confirmată ca fiind implementată efectiv în aplicație, dar acest dosar nu conține un citat verbatim din actul care reglementează explicit mecanismul de prorogare a termenelor fiscale (de regulă, Codul de procedură fiscală) — de aceea, mai jos descriem mecanismul ca fiind confirmat din comportamentul aplicației, nu dintr-un citat legal reprodus verbatim.

## Cum funcționează

1. Se calculează data nominală a termenului (de regulă ziua 25 a lunii următoare perioadei raportate, cu excepții pentru anumite tipuri de declarații).
2. Dacă acea dată cade sâmbătă, duminică, sau într-o zi de sărbătoare legală (fixă sau mobilă), termenul se mută pe următoarea zi lucrătoare.

**Exemplu, pentru 2026**: data de 25 octombrie 2026 cade duminică. Pentru o declarație cu termen nominal pe 25 ale lunii (de exemplu D112), termenul real devine luni, 26 octombrie 2026 — cu condiția ca 26 octombrie să nu fie, la rândul ei, o zi de sărbătoare legală.

## Ce se greșește în practică

- Se depune declarația cu întârziere, crezând greșit că, dacă data nominală cade în weekend, termenul „se pierde" sau se amână automat cu o săptămână — de fapt se mută doar până la prima zi lucrătoare imediat următoare.
- Se ignoră sărbătorile legale mobile (calculate după Paștele ortodox), care pot muta termenul cu mai mult de o zi față de o simplă mutare de weekend.

## Ce face iConta.eu

Funcția care calculează scadența fiecărei declarații mută automat data nominală pe următoarea zi lucrătoare ori de câte ori aceasta cade în weekend sau într-o zi de sărbătoare legală — calendarul de sărbători (zile fixe plus cele cinci zile mobile derivate din Paștele ortodox) e calculat pentru intervalul 2024–2099, deci acoperă integral 2026.

[iConta.eu](/)
