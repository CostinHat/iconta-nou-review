---
title: "Ce curs se folosește pentru verificarea plafonului cash la o plată în valută?"
description: "Cursul BNR aplicabil la încadrarea în plafoanele legale de încasări și plăți în numerar, atunci când operațiunea e în valută."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce curs se folosește pentru verificarea plafonului cash la o plată în valută?

Plafoanele de încasări și plăți în numerar din Legea nr. 70/2015 se aplică și operațiunilor efectuate în valută pe teritoriul României, iar legea spune explicit ce curs valutar se folosește pentru a verifica încadrarea în plafon.

## Temeiul legal

::: ghid-temei
„Prevederile prezentului capitol se aplică și operațiunilor de încasări și plăți în valută efectuate pe teritoriul României. Încadrarea în plafoanele prevăzute de prezentul capitol se efectuează în funcție de cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunilor de încasări sau plăți."
— Legea nr. 70/2015, art. 1 alin. (3) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Regula de aplicat:

- Pentru o încasare sau o plată în numerar făcută în valută (de exemplu EUR sau USD), suma se transformă în lei la **cursul BNR din ziua efectuării operațiunii** — nu la cursul din ziua facturii, nu la un curs mediu lunar și nu la cursul contabil folosit pentru înregistrarea diferențelor de curs.
- Suma astfel obținută în lei se compară cu plafoanele obișnuite din lege: 5.000 lei/10.000 lei (cash and carry) pentru încasări/plăți către o persoană, respectiv 10.000 lei/zi pentru operațiuni cu persoane fizice, așa cum rezultă din restul capitolului I al legii.
- Regula se aplică simetric — atât pentru încasările, cât și pentru plățile în valută — și pentru orice operațiune realizată pe teritoriul României, indiferent de moneda în care e denominată.

## Ce se greșește în practică

- Se folosește cursul din contract sau din factură pentru verificarea plafonului, în loc de cursul BNR din ziua efectivă a încasării/plății în numerar.
- Se presupune că plafoanele de numerar nu se aplică deloc operațiunilor în valută — legea spune expres contrariul, la art. 1 alin. (3).
- Se aplică un curs mediu sau un curs „de conveniență" atunci când în aceeași zi există mai multe operațiuni în valute diferite, în loc de cursul BNR comunicat pentru acea zi, pentru fiecare valută în parte.

## Ce face iConta.eu

Modulul de casierie din iConta.eu (`core/casa.py`) verifică plafoanele de numerar pe baza sumelor înregistrate în lei în registrul de casă. Pentru operațiunile introduse direct în valută, conversia la cursul BNR al zilei se face prin modulul de curs valutar al aplicației (`core/curs_bnr.py`), folosit consecvent și pentru alte calcule fiscale care depind de cursul zilei — nu există un curs separat, „de plafon", diferit de cursul BNR aplicat restului operațiunilor contabile.

[iConta.eu](/)
