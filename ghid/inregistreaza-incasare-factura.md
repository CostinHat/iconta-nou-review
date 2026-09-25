---
title: "Cum se înregistrează o încasare fără factură?"
description: "Ce este, din punct de vedere fiscal, o încasare primită înainte de a fi emisă factura (avans) și cum tratează TVA la încasare acest caz."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează o încasare fără factură?

Cea mai frecventă situație în care banii ajung la firmă înainte să existe o factură este avansul: clientul plătește parțial sau integral contravaloarea unei livrări/prestări care încă nu a avut loc. Legea o tratează explicit ca pe un eveniment separat de exigibilitate a TVA, indiferent dacă firma e sau nu înscrisă în sistemul TVA la încasare — iar pentru o firmă înscrisă, regula capătă o nuanță suplimentară.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: [...] b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora."
— Codul fiscal, art. 282 alin. (2) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Pentru o firmă în **regimul normal** de TVA, avansul e o excepție care grăbește exigibilitatea: taxa devine datorată la încasare, nu la livrare/facturare.
- Pentru o firmă **înscrisă în sistemul TVA la încasare**, exigibilitatea e oricum legată de încasare (art. 282 alin. 3) — avansul se încadrează firesc în aceeași regulă, ca o încasare parțială.
- Art. 282 alin. (8) precizează cum se extrage TVA din suma încasată: „fiecare încasare totală sau parțială se consideră că include și taxa aferentă" — deci TVA nu se adaugă peste sumă, ci se calculează prin sută mărită (sumă × cotă/(100+cotă)).
- Chiar dacă nu există încă o factură fiscală pentru livrare, încasarea trebuie evidențiată contabil imediat, cu TVA aferentă recunoscută ca exigibilă (sau, pentru avans acordat/primit, direct pe contul de TVA exigibil).

## Ce se greșește în practică

- Se așteaptă emiterea facturii de livrare pentru a înregistra și TVA, deși legea leagă exigibilitatea de data încasării avansului, nu de data facturii finale.
- Se calculează TVA-ul aplicând cota peste suma încasată, în loc de sută mărită — greșeală care produce o bază de impozitare umflată.
- Se presupune că regula avansului nu se aplică firmelor la TVA la încasare, pentru că "oricum TVA e la încasare" — de fapt regula rămâne valabilă, doar că nu mai e o excepție, ci coincide cu regula generală a regimului.
- Se omite înregistrarea contabilă a avansului până la emiterea facturii, ceea ce lasă TVA neevidențiată în perioada corectă.

## Ce face iConta.eu

iConta.eu are un modul dedicat de contabilizare a avansurilor (`core/avansuri.py`): un avans încasat de la client generează automat nota `4111 = % (419 + 4427)`, iar TVA merge direct pe contul de TVA exigibilă (4427), niciodată pe cel neexigibil (4428) — indiferent dacă firma aplică sau nu TVA la încasare. Motorul de calcul al sumei de TVA din încasare (sută mărită) e implementat separat, în `core/tva_incasare.py`.

De precizat onest: acest modul de avansuri e generic — nu are o ramură de cod condiționată explicit de flagul `tva_la_incasare` al firmei și nu citează în comentarii art. 282 alin. (3)/(8). Rezultatul practic (TVA direct pe 4427) e coerent cu formularea legii de mai sus, dar nu e o comportare verificată explicit ca fiind "regula specială TVA la încasare aplicată avansurilor" — e mai degrabă rezultatul firesc al faptului că orice avans e, prin definiție legală, o încasare parțială exigibilă imediat. Pentru structuri contractuale neobișnuite (avansuri parțiale multiple, avansuri în valută, avansuri restituite parțial), verifică punctual rezultatul înainte de a-l considera definitiv.

[iConta.eu](/)
