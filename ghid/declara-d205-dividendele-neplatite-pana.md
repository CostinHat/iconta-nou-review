---
title: "Se declară în D205 dividendele neplătite până la sfârșitul anului?"
description: "Răspuns direct, cu temei legal, la întrebarea dacă dividendele aprobate dar neîncasate de asociați trebuie totuși trecute în D205."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se declară în D205 dividendele neplătite până la sfârșitul anului?

Da. Faptul că un dividend aprobat spre distribuire nu a fost încă plătit asociaților nu îl scoate din obligația de declarare — doar mută termenul de plată a impozitului.

## Temeiul legal

::: ghid-temei
"[...] În cazul dividendelor/câștigurilor obținute ca urmare a deținerii de titluri de participare, distribuite, dar care nu au fost plătite acționarilor/asociaților/investitorilor până la sfârșitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câștig se plătește până la data de 25 ianuarie inclusiv a anului următor distribuirii."
— Codul fiscal, art. 97 alin. (7) (`anaf_surse/cod_fiscal_227_2015_consolidat.txt:9470-9474`)
:::

Legea nu condiționează declararea de plata efectivă a dividendului. Odată aprobată distribuirea (de exemplu prin hotărârea AGA/decizia asociatului unic, înregistrată contabil pe creditul contului 457), impozitul aferent devine datorat, indiferent dacă suma a ajuns sau nu la asociat până la 31 decembrie.

## Ce se greșește în practică

Se sare adesea peste raportarea acestor sume, pe raționamentul "nu s-a plătit nimic, deci nu am ce declara". Consecința este o declarație D205 incompletă pentru anul aprobării și, potențial, impozit nevirat la termenul legal de 25 ianuarie anul următor.

## Ce face iConta.eu

Onest: în acest moment, generatorul D205 din iConta (`core/d205.py`) construiește beneficiarii doar pentru sumele efectiv plătite (citite din contul 457, cu status de notă contabilă validată); un dividend distribuit dar cu suma plătită zero nu produce automat o linie în declarație. Acesta este un gol cunoscut și asumat ca atare la nivel de produs, nu o funcționalitate care rezolvă automat acest caz. Interfața iConta nu oferă în acest moment o opțiune de adăugare manuală a unui beneficiar la generarea D205, așa că, dacă aveți dividende distribuite dar neplătite la 31 decembrie, trebuie să vă asigurați separat de aplicație că impozitul aferent este declarat, pentru a nu pierde obligația.

[iConta.eu](/)
