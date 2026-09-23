---
title: Cum se contabilizează factura GitHub?
description: O factură GitHub e o achiziție de servicii electronice, dar tratamentul TVA (D300 sau D301) depinde de statutul de TVA al firmei și de unde e stabilit furnizorul — nu de faptul că factura vine din străinătate.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează factura GitHub?

Un abonament GitHub (Team, Enterprise, Copilot, Actions etc.) e, contabil, o cheltuială cu servicii. Ce contează fiscal nu e denumirea serviciului, ci un singur lucru: locul prestării, care determină cine datorează TVA și în ce declarație intră operațiunea.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă (...) este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice." — Codul fiscal (Legea 227/2015), art. 278 alin. (2)
:::

Pentru o firmă din România care cumpără un serviciu de la GitHub, locul prestării e în România, indiferent unde e stabilit furnizorul. De aici decurge, pentru un beneficiar impozabil din România, obligația de a trata operațiunea prin taxare inversă (art. 307 alin. (2) CF, dacă furnizorul e stabilit în alt stat membru UE) sau printr-o regulă înrudită (art. 307 alin. (6), dacă furnizorul nu e stabilit deloc în UE).

**Verifică pe fiecare factură** numele și adresa entității emitente. Nu presupune că GitHub facturează dintr-o anumită țară — entitatea de facturare poate diferi de la un client la altul, iar acest detaliu schimbă tipul de operațiune (tip 5 dacă furnizorul e stabilit în UE, tip 4 dacă nu e).

### Cum se declară, în funcție de statutul firmei

- **Firmă plătitoare de TVA (art. 316):** taxare inversă în D300, rd. 7 (colectat) + rd. 20 (deductibil) — operațiune net zero. D301 e blocat pentru acest profil.
- **Firmă neplătitoare de TVA:** dacă furnizorul e stabilit în UE, operațiunea intră la D301 secțiunea 4.1 (tip 5) și, automat, în D390 cu cod S. Dacă furnizorul nu e stabilit în UE, operațiunea intră la D301 secțiunea 4 (tip 4, art. 307 alin. (6)) și **nu** apare în D390.

### Exemplu de calcul (bază rotunjită la leu întreg)

Factură GitHub Team, 21 USD, curs BNR din ziua exigibilității 4,6000 lei/USD:

baza = round(21 × 4,6000; 0) = round(96,60; 0) = **97 lei**

Baza se rotunjește la leu întreg — nu la 96,60 lei sau la bani. TVA-ul se calculează apoi din baza rotunjită, la cota aleasă (21% standard, de la 1.08.2025).

## Ce se greșește în practică

- Se presupune că o factură în valută, de la un furnizor din afara României, nu intră deloc în TVA românească — fals; locul prestării rămâne România.
- Se rotunjește baza cu zecimale (la bani), nu la leu întreg, cum cere formula oficială a formularului (coloana 2 × coloana 4).
- Se introduce operațiunea în D301 fără să se verifice vectorul fiscal al firmei — la un plătitor de TVA, aplicația refuză explicit introducerea, pentru că operațiunea aparține D300, nu D301.

## Ce face iConta.eu

Ecranul de introducere D301 cere tipul operațiunii, valuta, valoarea, cursul și cota; baza nu se introduce manual — se recalculează la generarea declarației, din valoare × curs, rotunjit la leu întreg. Țara și codul de TVA ale furnizorului sunt opționale, dar dacă le completezi, operațiunea apare automat și în D390 (tip 5 → cod S). Pentru o firmă înregistrată ca plătitoare de TVA, introducerea unei operațiuni D301 e blocată la nivel de aplicație, cu mesajul explicit că achiziția aparține D300.

[iConta.eu](/)
