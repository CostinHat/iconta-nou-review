---
title: Cum elimin din D205 un beneficiar introdus din greșeală?
description: Dacă beneficiarul a fost adăugat manual, se elimină acea intrare înainte de regenerare. Dacă a apărut automat din contul 457, cauza e o notă contabilă greșită, care trebuie corectată la sursă, nu ștearsă direct din declarație.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum elimin din D205 un beneficiar introdus din greșeală?

Depinde de unde a apărut beneficiarul: dintr-o intrare manuală, sau automat din contul 457. Tratamentul e diferit în fiecare caz.

## Temeiul legal

::: ghid-temei
**Art. 97 alin. (7) din Codul fiscal**: „[...] Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...]" — declararea corectă, fără beneficiari în plus sau în minus, e parte din această obligație.
:::

## Dacă beneficiarul a fost introdus manual

D205 permite adăugarea manuală a unor beneficiari în afara celor citiți automat din contul 457 (util, de exemplu, pentru dividende distribuite dar neplătite la 31 decembrie). Dacă o astfel de intrare manuală a fost adăugată din greșeală, eliminarea ei înainte de generarea finală e simplă: se scoate acea intrare din setul de date folosit la generare, iar declarația se regenerează automat, fără ea.

## Dacă beneficiarul a apărut automat din contul 457

Aici cauza reală e aproape sigur o notă contabilă greșit înregistrată — un asociat greșit, o sumă greșită, sau o notă care nu ar fi trebuit validată. D205 nu are un ecran propriu de editare, pentru că se generează automat din asociați și din notele validate pe 457 — corectarea se face la sursă, în contabilitate, nu prin „ștergerea" directă a beneficiarului din formular.

## Dacă declarația a fost deja depusă la ANAF

Ca și în celelalte cazuri de corecție D205, aplicația nu generează în acest moment o declarație rectificativă — eliminarea unui beneficiar declarat greșit dintr-o declarație deja transmisă trebuie tratată prin mijloacele oficiale ale ANAF.

## Ce se greșește în practică

Se caută o funcție de „ștergere" direct pe declarația generată, în loc de a corecta datele sursă (nota contabilă de pe 457 sau intrarea manuală) — fără corectarea sursei, orice regenerare ulterioară aduce înapoi aceeași eroare.

## Ce face iConta.eu

D205 se generează integral din date — asociați cu cotă de participare, note contabile validate pe 457 și, opțional, beneficiari introduși manual — fără un ecran de editare directă a declarației finale. Eliminarea unui beneficiar greșit înseamnă întotdeauna corectarea sursei (nota contabilă sau intrarea manuală), urmată de regenerare.

[iConta.eu](/)
