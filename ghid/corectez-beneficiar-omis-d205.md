---
title: Cum corectez un beneficiar omis din D205?
description: Cel mai frecvent caz de beneficiar omis e un dividend distribuit dar neplătit până la 31 decembrie — aplicația nu îl include automat. Legea cere însă explicit includerea lui în declarația anului distribuirii; trebuie adăugat manual.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez un beneficiar omis din D205?

Cel mai probabil motiv pentru care un beneficiar lipsește din D205 generată automat: dividendul i-a fost **distribuit**, dar nu i-a fost **plătit** până la 31 decembrie — iar generatorul, în acest moment, include în declarație doar beneficiarii cu sumă efectiv plătită mai mare de zero.

## Temeiul legal

::: ghid-temei
Instrucțiunile oficiale de completare D205 (OPANAF 179/2022, secțiunea despre impozitul pe veniturile din dividende): „Impozitul aferent dividendelor distribuite, dar care nu au fost plătite acționarilor sau asociaților până la sfârșitul anului în care s-a aprobat distribuirea acestora se cuprinde în declarația aferentă perioadei în care s-a aprobat distribuirea dividendelor."
:::

## Ce înseamnă practic

Legea e clară: chiar dacă dividendul nu a fost plătit până la 31 decembrie, impozitul aferent trebuie inclus în declarația anului în care distribuirea a fost **aprobată**, nu amânat până în anul plății efective. Însă aplicația, în forma ei actuală (verificată la 17.09.2026), filtrează automat la generare doar beneficiarii cu sumă plătită mai mare de zero — un dividend distribuit dar neplătit nu produce automat o linie în declarație.

**Ce trebuie să faceți**: verificați, înainte de generarea finală a D205, toate distribuirile din an (înregistrate pe creditul contului 457) care nu au fost urmate de o plată completă până la 31 decembrie. Pentru fiecare astfel de caz, beneficiarul trebuie adăugat manual la generare — aplicația are un parametru dedicat pentru beneficiari introduși manual, în afara celor citiți automat din contul 457.

## Ce se greșește în practică

Se presupune că dividendul „va apărea oricum" în declarația anului în care e efectiv plătit, deci se lasă nedeclarat în anul distribuirii — contrar regulii de mai sus, care cere includerea lui în anul aprobării distribuirii, nu al plății.

## Ce face iConta.eu

Generatorul D205 include automat doar beneficiarii cu sumă plătită peste zero, citiți din contul 457. Pentru cazul „distribuit, dar neplătit la 31 decembrie" — cel mai frecvent motiv al unui beneficiar omis — aplicația nu face încă acest adăugat automat; contabilul trebuie să identifice manual situația și să adauge beneficiarul folosind parametrul de intrare manuală disponibil la generare, ca să nu piardă obligația fiscală din declarație.

[iConta.eu](/)
