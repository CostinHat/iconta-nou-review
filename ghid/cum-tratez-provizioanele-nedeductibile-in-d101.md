---
title: Cum tratez provizioanele nedeductibile în D101?
description: Provizioanele nedeductibile (litigii, dezafectare, restructurare, altele, ajustări de stoc, partea nedeductibilă din ajustările de creanțe) se adaugă manual la rândurile de cheltuieli nedeductibile din D101 — aplicația nu preia automat aceste sume din notele contabile.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum tratez provizioanele nedeductibile în D101?

Un provizion nedeductibil fiscal (litigii, dezafectare, restructurare, altele, sau ajustări pentru deprecierea stocurilor) rămâne totuși o cheltuială înregistrată contabil (6812 sau 6814). La calculul impozitului pe profit, această cheltuială trebuie adăugată înapoi la rezultatul contabil, prin rândurile de cheltuieli nedeductibile din declarația D101.

## Temeiul legal

::: ghid-temei
"cheltuielile cu provizioane/ajustări pentru depreciere și rezerve, în limita prevăzută la art. 26;"

"Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru
depreciere, numai în conformitate cu prezentul articol, astfel: [...]"
:::

## Ce se trece manual în D101

Rândurile "Cheltuieli nedeductibile" din D101 (P23-P33, cumulate în P34) preiau, printre altele, valoarea provizioanelor și ajustărilor nedeductibile constituite în exercițiul respectiv:

- integralul provizioanelor pentru litigii (1511), dezafectare (1513), restructurare (1514), alte provizioane (1518) — nu se regăsesc în lista de deduceri de la art. 26;
- integralul ajustărilor pentru deprecierea stocurilor (conturi 39x) — de asemenea, în afara listei de la art. 26;
- partea **nedeductibilă** dintr-o ajustare de creanță aflată sub pragul de deducere (de exemplu, 70% dintr-o ajustare dedusă 30%, sau 100% dintr-o ajustare sub pragul de 270 de zile ori la un client afiliat/garantat);
- partea din provizionul pentru garanții care depășește cota contractuală de garanție.

::: ghid-exemplu
O firmă constituie o ajustare de creanță de 8.000 lei (client negarantat, neafiliat, 300 de zile neîncasată). Deducerea admisă e 30%, adică 2.400 lei. Diferența de 5.600 lei se adaugă la rândurile de cheltuieli nedeductibile din D101, chiar dacă întreaga sumă de 8.000 lei a fost înregistrată contabil pe cheltuieli (6814).
:::

## Ce se greșește în practică

- Se presupune că aplicația de contabilitate calculează automat rândul de cheltuieli nedeductibile pornind de la soldurile conturilor 6812/6814 — de regulă, această legătură nu există automat, iar valorile trebuie introduse manual.
- Se raportează în D101 doar provizioanele complet nedeductibile, omițând partea nedeductibilă a celor parțial deductibile (ex. 70% din ajustarea de creanță dedusă 30%).
- Se omite verificarea cotei contractuale de garanție pentru provizionul de garanții, raportând întreaga sumă ca deductibilă.
- Se dublează suma — se trece cheltuiala nedeductibilă în D101 și, separat, se ajustează greșit și rezultatul contabil, generând o corecție dublă.

## Ce face iConta.eu

Rândurile D101 de cheltuieli nedeductibile (P23-P33, cumulate în P34) sunt **input manual** în `core/d101.py` — funcția citește direct valorile primite de la utilizator (`g("P23")` ... `g("P33")`) și nu importă nimic din `core/provizioane.py`. Nu există niciun calcul automat pornind de la soldurile conturilor 6812/6814 sau de la flagul `deductibil` întors de `nota_provizion` ori `deductibilitate_creanta`. În consecință, întreaga analiză de mai sus (identificarea provizioanelor nedeductibile și a părții nedeductibile din cele parțial deductibile) trebuie făcută separat, iar rezultatul introdus manual în rândurile corespunzătoare din D101.

[iConta.eu](/)
