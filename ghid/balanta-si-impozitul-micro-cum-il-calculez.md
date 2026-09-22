---
title: Balanța și impozitul micro: cum îl calculez
description: Impozitul micro se determină pornind de la rulajul conturilor de venituri din balanța de verificare a trimestrului (70x/75x/76x minus 709), cu cotă de 1%.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Balanța și impozitul micro: cum îl calculez

Balanța de verificare e sursa cea mai directă pentru a estima „din ochi" impozitul micro datorat, dacă știți exact ce rulaje trebuie citite și pentru ce perioadă. Ghidul acesta arată pas cu pas cum se leagă balanța de suma din D100.

## Temeiul legal

::: ghid-temei
**CF art. 53 alin. (1):**
> „Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie **veniturile din orice
> sursă**, din care se scad: a) veniturile aferente costurilor stocurilor de produse; b) veniturile
> aferente costurilor serviciilor în curs de execuție; ... j) valoarea reducerilor comerciale acordate
> ulterior facturării, înregistrate în contul «709»..."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt:6480-6519`

**CF art. 51 alin. (1):**
> „Cota de impozit pe veniturile microîntreprinderilor este de 1%."
— sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.html`
:::

## Ce rulaje se citesc din balanță

Din balanța de verificare a trimestrului se însumează rulajele creditoare ale conturilor de venituri relevante: clasa 70x (venituri din vânzări de produse, mărfuri, servicii), 75x (alte venituri din exploatare) și 76x (venituri financiare). Din suma obținută se scade rulajul contului 709 (reduceri comerciale acordate ulterior facturării) — singura deducere din art. 53 alin. (1) care apare frecvent la firmele mici, celelalte (stocuri, servicii în curs de execuție etc.) fiind mai rare.

Punctul critic: se ia **rulajul trimestrului curent**, nu soldul cumulat de la începutul anului. Balanța afișează de regulă și „rulaj cumulat" și „rulaj curent" — pentru D100 interesează al doilea.

::: ghid-exemplu
Balanța trimestrului III arată rulaj creditor cont 707 = 80.000 lei, cont 708 = 2.000 lei, cont 709 = 3.000 lei (reduceri comerciale acordate). Baza impozabilă = 80.000 + 2.000 − 3.000 = 79.000 lei. Impozitul datorat = 79.000 × 1% = 790 lei.
:::

## Ce se greșește în practică

- Se ia rulajul cumulat de la 1 ianuarie din balanță, în loc de rulajul strict al trimestrului curent — dublează sau triplează baza.
- Se omite scăderea contului 709 din totalul veniturilor.
- Se includ în bază venituri care ar trebui excluse conform art. 53 alin. (1) (de exemplu, venituri din anularea provizioanelor, în anumite situații enumerate de lege).
- Se citește balanța „la data plății", nu balanța trimestrului de raportare, ceea ce introduce venituri din trimestrul următor.

## Ce face iConta.eu

`d100.pull()` citește direct din înregistrările contabile ale firmei — nu dintr-o balanță introdusă manual — veniturile aferente exact perioadei trimestrului de raportare, pe conturile 70x/75x/76x minus 709, și le transmite motorului de calcul (`deriva_obligatii`) care aplică cota de 1%. Suma rezultată e apoi confruntată automat, printr-o a doua cale de calcul independentă (`d100_reconciliere.verifica_reconciliere`, recalcul direct din `inregistrari_linii`), înainte ca declarația să poată fi generată — deci diferența dintre „ce arată balanța" și „ce declară aplicația" ar trebui să fie zero, dacă înregistrările contabile sunt corecte.

[iConta.eu](/)
