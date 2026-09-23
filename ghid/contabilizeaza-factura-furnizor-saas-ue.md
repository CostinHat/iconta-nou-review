---
title: Cum se contabilizează factura unui furnizor SaaS din UE?
description: Un abonament software cumpărat de la un furnizor stabilit în alt stat membru UE e o achiziție de servicii intracomunitare — se declară diferit la un plătitor și la un neplătitor de TVA, cu intrare automată în D390 pentru neplătitor.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se contabilizează factura unui furnizor SaaS din UE?

Indiferent de tipul aplicației (facturare, marketing, design, gestiune de proiect), un abonament cumpărat de la un furnizor SaaS stabilit în alt stat membru UE urmează același mecanism fiscal: servicii intracomunitare, cu locul prestării în România.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă (...) este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice." — Codul fiscal (Legea 227/2015), art. 278 alin. (2)
:::

Pentru firma din România, locul prestării e România — beneficiarul, nu furnizorul, datorează TVA (art. 307 alin. (2) CF), pentru că furnizorul e stabilit în alt stat membru. Rezultă un singur lucru sigur din start: nu se plătește (și nu se cere) TVA furnizorului pe factură — mecanismul e taxare inversă, la beneficiar.

### Cum se declară

- **Firmă plătitoare de TVA (art. 316):** taxare inversă în D300 (rd. 7 + rd. 20), operațiune net zero. D301 e blocat pentru acest profil de firmă.
- **Firmă neplătitoare de TVA:** D301, secțiunea 4.1 (tip 5), cu obligație de înregistrare prin art. 317 **înainte** de primul abonament cumpărat, fără plafon valoric. Operațiunea intră automat și în D390, cu cod S.

### Exemplu de calcul

Abonament SaaS, 49,00 EUR/lună, curs zilei exigibilității 4,9700 lei/EUR:

baza = round(49,00 × 4,9700; 0) = round(243,53; 0) = **244 lei**

Baza se rotunjește la leu întreg — nu se declară cu zecimale de bani. TVA-ul se calculează din bază, la cota aplicabilă (21% standard sau 11% redusă, după caz, conform Legii 141/2025).

## Ce se greșește în practică

- Se plătește TVA local (RO) furnizorului, deși mecanismul corect e taxarea inversă — furnizorul UE ar trebui să factureze fără TVA, cu mențiunea privind taxarea inversă.
- Se amână înregistrarea prin art. 317 „până apare mai multe cheltuieli de acest fel" — obligația nu depinde de valoare, ci apare de la primul abonament.
- Se lasă necompletate câmpurile de țară și cod TVA ale furnizorului, ceea ce lasă operațiunea în afara D390.

## Ce face iConta.eu

Ecranul de introducere D301 cere tipul operațiunii, valuta, valoarea, cursul și cota (cota redusă apare doar dacă e configurată pentru perioadă, ca să nu se ofere o valoare falsă). Țara și codul de TVA ale furnizorului sunt opționale, dar completarea lor duce automat operațiunea și în D390. La generare, baza se recalculează din valoare × curs, rotunjită la leu întreg, iar declarația nu se generează pentru o perioadă fără nicio operațiune introdusă.

[iConta.eu](/)
