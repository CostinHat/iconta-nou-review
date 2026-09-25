---
title: "Cum se declară în D301 o factură omisă din luna anterioară?"
description: "Ce prevede legea despre corectarea declarațiilor fiscale atunci când o achiziție intracomunitară a fost omisă dintr-un D301 deja depus."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară în D301 o factură omisă din luna anterioară?

D301 e decontul special de TVA depus de persoanele neînregistrate normal în scopuri de TVA (art. 316 Cod fiscal), dar care fac achiziții intracomunitare sau alte operațiuni cu taxare inversă. Dacă o astfel de achiziție a fost omisă din D301-ul lunii în care a avut loc, factura nu se „strecoară" în decontul lunii curente — corectarea se face pe perioada la care se referă, printr-o declarație rectificativă.

## Temeiul legal

::: ghid-temei
„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...]
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1) și (3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Aplicat la D301:

- Achiziția omisă nu se adaugă la operațiunile lunii curente, chiar dacă e descoperită abia acum — ea aparține lunii în care a avut loc, conform documentului justificativ.
- Corectarea se face prin depunerea unei declarații D301 rectificative pentru luna respectivă, în interiorul termenului de prescripție a dreptului organului fiscal de a stabili creanțe fiscale.
- Formularul D301 (OPANAF 592/2016, modificat prin OPANAF 779/2024) are un câmp dedicat pentru marcarea declarației ca rectificativă — corectarea nu e o depunere „ca și cum ar fi prima dată", ci una explicit semnalată ca atare.

## Ce se greșește în practică

- Se include factura omisă în D301 al lunii curente, „ca să nu se piardă" — ceea ce denaturează atât luna curentă, cât și luna reală a operațiunii.
- Se presupune că, fiind o sumă mică, corectarea nu merită efortul unei rectificative — dar obligația de raportare corectă nu are prag de minimis.
- Se uită bifarea declarației ca rectificativă, ceea ce poate genera respingeri sau neconcordanțe la validare.

## Ce face iConta.eu

Modulul D301 din iConta.eu (`core/d301.py`) generează decontul din operațiunile introduse pentru perioada respectivă și include suportul pentru declarația rectificativă (bifa introdusă de OPANAF 779/2024). Depunerea efectivă a unei rectificative pentru o lună anterioară rămâne o acțiune explicită a contabilului, pornind de la achiziția omisă adăugată retroactiv pe luna corectă — aplicația nu detectează singură facturile omise.

[iConta.eu](/)
