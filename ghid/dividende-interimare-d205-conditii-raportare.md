---
title: Dividende interimare la D205 - condiții de raportare
description: D205 generată automat citește doar dividendele contabilizate pe contul 457; dividendele interimare plătite și impozitate în cursul anului prin contul 456, dar neregularizate până la 31 decembrie, nu apar deloc în declarația generată automat.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Dividende interimare la D205 - condiții de raportare

Dividendele interimare — distribuite trimestrial, în cursul anului, pe baza situațiilor financiare interimare — se contabilizează diferit față de dividendele anuale, iar această diferență contabilă are un efect direct și important asupra a ceea ce apare automat în D205. Dacă distribuiți dividende interimare, citiți acest ghid cu atenție înainte de a genera declarația.

## Temeiul legal

::: ghid-temei
„Impozitul aferent dividendelor distribuite, dar care nu au fost plătite acţionarilor sau asociaţilor până la sfârşitul anului în care s-a aprobat distribuirea acestora se cuprinde în declaraţia aferentă perioadei în care s-a aprobat distribuirea dividendelor." (OPANAF 179/2022, Cap.V dividende, l.398-400)

„În cazul dividendelor distribuite în baza situaţiilor financiare interimare întocmite în cursul anului 2025/anului fiscal modificat care începe în anul 2025, cota de impozit pe dividende este de 10%, fără recalcularea impozitului pe dividendele respective, după regularizarea acestora pe baza situaţiilor financiare anuale aferente exerciţiului financiar 2025..., aprobate potrivit legii." (Legea 141/2025, art.VII alin.(2))
:::

## Cum se contabilizează dividendele interimare și ce se întâmplă în D205

Dividendele anuale (aprobate pe baza situațiilor financiare anuale) se contabilizează pe contul 457: distribuirea brută (`1171=457`), impozitul (`457=446`), plata netă (`457=5121`). Dividendele **interimare** urmează însă un circuit contabil diferit, pe contul 456: distribuirea brută (`463=456`), impozitul (`456=446`), plata netă (`456=5121`). Abia după aprobarea situațiilor financiare anuale — de regulă în anul următor — se face regularizarea, care mută sumele pe 457 (`1171=457` pentru dividendul anual aprobat, `457=463` pentru compensarea cu interimarele deja acordate).

Generarea automată a D205 citește exclusiv mișcările din contul 457. Dacă distribuiți și plătiți dividende interimare în cursul anului X, dar regularizarea (nota care mută sumele pe 457) nu se face până la 31 decembrie al anului X — ceea ce e situația normală, pentru că regularizarea depinde de aprobarea situațiilor financiare anuale, aprobare care are loc de regulă abia în anul X+1 — declarația D205 pentru anul X, generată automat, **nu va conține deloc acei beneficiari și acel impozit**, deși impozitul a fost deja reținut și virat real prin contul 456.

::: ghid-exemplu
O firmă distribuie și plătește dividende interimare unui asociat în luna august 2026, reținând și virând corect impozitul prin contul 456. Situațiile financiare anuale pentru 2026 se aprobă abia în aprilie 2027, moment în care se face regularizarea (mutarea pe 457). Dacă generați D205 pentru 2026 direct din aplicație, în februarie 2027, acel asociat și acel impozit nu vor apărea în declarația generată automat, pentru că la acel moment regularizarea încă nu a avut loc.
:::

## Ce se greșește în practică

- Se generează D205 direct din fluxul automat, fără să se verifice dacă toate dividendele interimare din anul respectiv au fost deja regularizate (mutate pe 457) înainte de generare.
- Se presupune că, dacă impozitul a fost deja reținut și virat prin contul 456, el va apărea automat undeva în D205 — de fapt, fără regularizare, nu apare nicăieri în declarația generată automat.
- Se confundă termenul de regularizare contabilă (după aprobarea situațiilor financiare anuale) cu termenul de depunere a D205 (ultima zi de februarie a anului următor) — al doilea vine adesea înaintea primului.
- Se ignoră faptul că beneficiarii de dividende interimare neregularizate trebuie introduși manual în declarație, dacă regularizarea nu se poate face la timp.

## Ce face iConta.eu

Calea automată de generare a D205 citește exclusiv notele contabile validate cu mișcări pe contul 457 (atât pentru calculul bazei/impozitului, cât și pentru a doua cale de recalcul independent, și pentru semaforul care decide dacă declarația e datorată). Dividendele interimare, contabilizate pe 456/463 până la regularizare, nu sunt atinse de această citire automată. Dacă nu apucați să regularizați dividendele interimare (nota `1171=457` + `457=463`) până la generarea D205, aveți două opțiuni: fie faceți regularizarea contabilă înainte de a genera declarația, fie introduceți beneficiarii respectivi manual în declarație. Beneficiarii introduși manual nu trec prin recalculul automat din contul 457, dar rămân supuși unei verificări interne de consistență (impozitul trebuie să corespundă aproximativ cotei de impozit aplicate la bază, pe cota anului curent sau a anului anterior, pentru exact acest caz de distribuire-anterioară/plată-curentă).

[iConta.eu](/)
