---
title: Cum se contabilizează factura Amazon Web Services din UE?
description: Când AWS facturează dintr-o entitate stabilită în Uniunea Europeană, achiziția e servicii intracomunitare (tip 5) — cu obligații diferite pentru un plătitor și pentru un neplătitor de TVA, plus intrare automată în D390.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează factura Amazon Web Services din UE?

Dacă factura AWS provine de la o entitate stabilită într-un alt stat membru UE, operațiunea intră la categoria „servicii intracomunitare" — Secțiunea 4.1 din formularul special de TVA, distinctă de restul operațiunilor de la art. 307.

## Temeiul legal

::: ghid-temei
Secțiunea 4.1 din formular: „Achiziții de servicii intracomunitare, pentru care beneficiarul este obligat la plata TVA conform art. 307 alin. (2)" — OPANAF 592/2016, Anexa 1. Instrucțiunile de completare precizează că se aplică serviciilor de la prestatori „stabiliți pe teritoriul (...) dar care sunt stabilite în Comunitate" — OPANAF 592/2016, Anexa 2, Instrucțiuni.
:::

Distincția contează: Secțiunea 4.1 (tip 5) e rezervată explicit prestatorilor **stabiliți în UE**. Dacă entitatea care emite factura AWS e stabilită în afara Uniunii, operațiunea nu se mai încadrează aici, ci la tip 4 (art. 307 alin. (6)) — cu efecte diferite, în special asupra D390.

### Cum se declară, în funcție de statutul TVA

- **Firmă plătitoare de TVA (art. 316):** taxare inversă în D300, rd. 7 (colectat) + rd. 20 (deductibil), operațiune net zero. D301 nu se completează pentru acest profil.
- **Firmă neplătitoare de TVA:** D301, secțiunea 4.1 (tip 5), cu obligația de înregistrare specială prin art. 317 înainte de primirea primului serviciu, fără plafon. Operațiunea intră automat și în D390, cu cod S — un neplătitor înregistrat doar prin art. 317 depune, în aceeași lună, ambele declarații.

### Exemplu de calcul

Factură AWS EU, 250,00 EUR, curs zilei exigibilității 4,9773 lei/EUR:

baza = round(250,00 × 4,9773; 0) = round(1.244,325; 0) = **1.244 lei**

Baza intră în D301 rotunjită la leu întreg; TVA-ul se calculează din bază, la cota aplicabilă perioadei (21% standard, de la 1.08.2025, conform Legii 141/2025).

## Ce se greșește în practică

- Se presupune automat „furnizor UE → tot ce cumpăr de la el e tip 5" — regula se aplică strict serviciilor de la art. 307 alin. (2), nu oricărei achiziții de la același furnizor.
- Se omite codul de TVA al furnizorului la introducere, crezând că D390 se completează separat — de fapt, câmpul declanșează derivarea automată în D390.
- Se calculează baza cu două zecimale (bani) în loc de rotunjire la leu întreg.

## Ce face iConta.eu

La introducerea unei operațiuni tip 5, câmpurile de țară și cod TVA ale furnizorului sunt opționale, dar completarea lor produce automat operațiunea corespunzătoare în D390, cu codul S. Baza se recalculează la generare, din valoare × curs, rotunjită la leu întreg — nu se stochează la introducere, ca să nu rămână „înghețată" pe o valoare intermediară. Pentru o firmă plătitoare de TVA, ecranul refuză explicit introducerea, cu mesajul că achiziția aparține D300.

[iConta.eu](/)
