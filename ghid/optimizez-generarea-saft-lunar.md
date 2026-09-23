---
title: "Cum optimizez generarea SAF-T lunar"
description: "Ce poți controla la fiecare generare D406 lunară ca fișierul să iasă corect din prima încercare, și ce limite tehnice trebuie să știi din timp."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum optimizez generarea SAF-T lunar

„Optimizarea" generării SAF-T (D406) nu înseamnă un buton magic, ci trei lucruri pe care le controlezi înainte de a apăsa generarea: periodicitatea corectă, validarea înainte de depunere și cunoașterea a ceea ce fișierul chiar conține.

## Temeiul legal

::: ghid-temei
„Contribuabilii/Plătitorii transmit Declaraţia informativă D406 lunar sau trimestrial, urmând perioada fiscală aplicabilă pentru taxa pe valoarea adăugată (TVA). Contribuabilii care au ca perioadă fiscală aplicabilă pentru taxa pe valoarea adăugată semestrul sau anul transmit Declaraţia informativă D406 trimestrial." — OPANAF nr. 1783/2021, Anexa 4, pct. 2
:::

„Contribuabilii care nu sunt înregistraţi în scopuri de TVA transmit Declaraţia informativă D406 trimestrial." (OPANAF 1783/2021, Anexa 4, pct. 3)

Primul pas al „optimizării" e să nu generezi declarația pe periodicitatea greșită. iConta stabilește automat tipul de fereastră (`core/common.py::fereastra_d406`) după aceeași logică din Anexă: dacă firma nu e plătitoare de TVA, sau are TVA semestrial/anual, fereastra e forțată trimestrial; altfel urmează tipul perioadei de TVA a firmei. Nu există o variantă „anuală" a raportării periodice — anual se depune doar secțiunea Active (Assets), separat, la termenul situațiilor financiare.

## Ce se greșește în practică

- Se generează și se depune fișierul fără să fie validat înainte, ceea ce mută descoperirea erorilor de structură din faza de pregătire (unde se pot corecta liniștit) în faza de depunere (unde erorile costă timp și, potențial, amendă).
- Se presupune că fișierul SAF-T conține automat tot ce a fost înregistrat în contabilitate, inclusiv plățile — fals în stadiul tehnic actual (vezi mai jos).
- Nu se ține cont de faptul că, pentru livrări, codurile de taxă (TaxCode) diferă înainte și după 01.08.2025 (Legea 141/2025) — o generare „optimizată" nu amestecă regulile vechi cu cele noi pe aceeași perioadă.

## Ce face iConta.eu

Generatorul D406 (`core/d406.py`) produce Header, MasterFiles și GeneralLedgerEntries complet din XSD, iar SourceDocuments (facturi de vânzare/achiziție) cu linii reale pe produs (cantitate, UM, preț, descriere, cotă), reconciliate obligatoriu cu antetul declarației — nu doar totaluri agregate. Identitatea partenerului urmează nomenclatorul (00/01/02+cod, 03+CNP, 04+nume). Codurile de taxă pentru livrări sunt aplicate „period-aware", pe data facturii, ținând cont de schimbarea din Legea 141/2025.

Validarea nu se face cu un instrument generic, ci cu `DUKIntegrator_AnLunaUI.jar` (validatorul oficial), integrat direct în aplicație — pasul de validare înainte de depunere e parte din flux, nu un instrument extern separat de gestionat manual.

Onest, ca să nu optimizezi pe baza unor așteptări greșite: secțiunea **Payments** (plăți) rămâne neemisă — codul de generare există, dar nu se populează încă din sursă, în lipsa unei mapări a trezoreriei; **MovementOfGoods** iese goală (self-closed); **AssetTransactions** lipsește (opțională conform XSD). Declarația e depunerea pe zero-plăți, dar incompletă pentru firmele cu plăți de raportat în această secțiune — de știut din timp, nu de descoperit la validare.

[iConta.eu](/)
