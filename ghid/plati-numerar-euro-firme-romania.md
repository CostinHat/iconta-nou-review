---
title: "Se pot face plăți în numerar în euro între firme în România?"
description: "Legea 70/2015 aplică aceleași plafoane de numerar și operațiunilor în valută efectuate pe teritoriul României, la cursul BNR din ziua plății."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se pot face plăți în numerar în euro între firme în România?

Da, plățile în euro (sau altă valută) în numerar între firme sunt permise pe teritoriul României, dar **nu scapă** de plafoanele din Legea 70/2015 — legea le tratează explicit la fel ca plățile în lei, cu încadrarea sumei făcută la cursul de schimb al zilei operațiunii.

## Temeiul legal

::: ghid-temei
„(3) Prevederile prezentului capitol se aplică și operațiunilor de încasări și plăți în valută efectuate pe teritoriul României. Încadrarea în plafoanele prevăzute de prezentul capitol se efectuează în funcție de cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunilor de încasări sau plăți."
— Legea 70/2015, art. 1 alin. (3) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce înseamnă concret pentru o plată în euro între două firme din România:

- Plafonul de **5.000 lei/zi** pentru plăți către un singur furnizor (art. 3) se aplică și în euro — dar convertit, la **cursul BNR al zilei plății**, nu la un curs fix sau la cursul de la data facturii.
- Interdicția de **fragmentare** a plăților pentru a evita plafonul (art. 2 lit. b)) se aplică identic, indiferent de moneda folosită — plata unei facturi de 6.000 lei echivalent euro, în două tranșe a câte 3.000 lei, e la fel de interzisă ca în lei.
- Excepțiile din capitolul I (Trezoreria Statului, instituții de credit, instituții de plată autorizate, case de schimb valutar pentru operațiunile lor specifice) rămân valabile și pentru operațiunile în valută.
- Rezultă că nu există o cale de a folosi euro pentru a „ocoli" plafonul de numerar aplicabil în lei — legea a fost scrisă explicit ca să prevină exact acest ocol.

## Ce se greșește în practică

- Se presupune că plafoanele din Legea 70/2015 se aplică doar plăților în lei, iar plățile în valută ar fi „în afara legii" — art. 1 alin. (3) spune contrariul, explicit.
- Se convertește suma la un curs arbitrar sau la cursul de la data facturii, nu la **cursul BNR din ziua efectuării plății** — diferența de curs poate scoate operațiunea din plafonul legal fără ca firma să-și dea seama.
- Se fac plăți repetate în euro, în tranșe mici, către același furnizor în aceeași zi, considerând că fiecare tranșă e „sub plafon" — interdicția de fragmentare se aplică indiferent de monedă, la suma totală a tranzacției.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu convertește automat operațiunile în valută la cursul BNR al zilei** pentru a verifica încadrarea în plafoanele de numerar — modulul de casierie (`core/casa.py`) aplică plafoanele curente din Legea 70/2015 (actualizate cu Legea 239/2025) pe operațiunile introduse, dar verificarea specifică a unei plăți în euro raportate la cursul zilei rămâne, la data acestui ghid, o încadrare pe care contabilul o face manual.

[iConta.eu](/)
