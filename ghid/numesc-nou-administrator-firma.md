---
title: "Cum numesc un nou administrator în firmă"
description: "Cum se numește legal un nou administrator al unui SRL, cine decide și ce pași urmează la Registrul Comerțului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum numesc un nou administrator în firmă

Numirea unui nou administrator la un SRL nu e o simplă formalitate internă — decizia aparține asociaților, se ia cu o anumită majoritate și trebuie înregistrată la Registrul Comerțului pentru a fi opozabilă terților.

## Temeiul legal

::: ghid-temei
„Asociații care reprezintă majoritatea absolută a capitalului social pot alege unul sau mai mulți administratori dintre ei, fixându-le puterile, durata însărcinării și eventuala lor remunerație, afară numai dacă prin actul constitutiv nu se dispune altfel."
— Legea 31/1990 (legea societăților), art. 77 alin. (1) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Ce presupune, concret, procedura:

- Societatea e administrată de unul sau mai mulți administratori, asociați sau neasociați, numiți **prin actul constitutiv** sau, ulterior, **de adunarea generală** a asociaților (art. 197 alin. 1).
- Numirea unui nou administrator (altul decât prin actul constitutiv inițial) se face cu votul asociaților care reprezintă majoritatea absolută a capitalului social, dacă actul constitutiv nu prevede o majoritate diferită.
- Odată numit, administratorul trebuie înscris la Registrul Comerțului printr-o cerere de mențiuni, însoțită de hotărârea asociaților și de actul de identitate/specimenul de semnătură — fără această înregistrare, numirea nu e opozabilă terților.

## Ce se greșește în practică

- Se consideră administratorul „numit" din momentul semnării hotărârii asociaților, fără depunerea cererii de mențiuni la Registrul Comerțului — până la înregistrare, terții (bănci, ANAF, parteneri) nu au obligația să recunoască noua calitate.
- Se confundă majoritatea necesară pentru numire cu cea pentru revocare — revocarea administratorilor numiți prin actul constitutiv poate necesita o procedură diferită de simpla majoritate absolută.
- Se omite actualizarea vectorului fiscal și a datelor declarative (D112, dacă noul administrator e remunerat) după schimbarea de administrator.

## Ce face iConta.eu

iConta.eu nu automatizează procedura de numire a administratorului la Registrul Comerțului — aceasta rămâne o formalitate juridică separată, în afara aplicației. Aplicația oferă evidența contabilă generală (state de plată, declarații), inclusiv posibilitatea de a genera documente pentru un administrator remunerat, dar depinde de completarea corectă a datelor firmei (`core/vector_fiscal_api.py`, ecranul „Date firmă") — un test intern al codului (`test_document_fara_administrator.py`) confirmă că aplicația semnalează explicit lipsa datelor de administrator la generarea documentelor care le necesită, în loc să le lase necompletate tăcut.

[iConta.eu](/)
