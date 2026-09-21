---
title: Ce curs valutar folosești pentru o factură în valută
description: Pentru o factură în valută, cursul de TVA este ultimul curs BNR comunicat în ziua anterioară (valabil pentru ziua operațiunii), conform art. 290 alin. (2) din Codul fiscal și pct. 35 din Normele HG 1/2016. Cursul se fixează la data exigibilității și nu se recalculează la încasare.
published: 2026-09-21
modified: 2026-09-21
poarta: v1
functionalitate: F025
---

# Ce curs valutar folosești pentru o factură în valută?

Când emiți o factură în euro sau altă valută, baza de TVA trebuie exprimată în lei. Întrebarea nu e „ce curs iau azi", ci „care curs, de la ce dată" — iar răspunsul e fixat de lege, nu de banca ta sau de cursul din ziua în care încasezi.

## Temeiul legal

::: ghid-temei
**Cursul aplicabil — art. 290 alin. (2) din Codul fiscal (Legea 227/2015):** *„Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, valabil la data la care intervine exigibilitatea taxei."*

**Ce înseamnă „ultimul curs comunicat" — pct. 35 alin. (1) din Normele metodologice (HG 1/2016):** *„prin ultimul curs de schimb comunicat de Banca Națională a României se înțelege cursul de schimb comunicat de respectiva bancă în ziua anterioară și care este valabil pentru operațiunile care se vor desfășura în ziua următoare."*
:::

## Regula concretă

- **Cursul se ia din ziua anterioară.** BNR comunică în cursul unei zile cursul valabil pentru ziua următoare. Pentru o operațiune cu data X, cursul de TVA este cel publicat de BNR în ziua bancară anterioară (cel mai recent curs comunicat cu dată de valabilitate ≤ X).
- **Momentul de referință e exigibilitatea taxei**, de regulă data faptului generator (livrare/prestare), nu data la care emiți efectiv factura dacă aceasta e ulterioară.
- **Cursul se fixează o singură dată.** Odată stabilit la exigibilitate, nu se recalculează la încasare și nu se ajustează dacă între timp cursul s-a mișcat. Diferența dintre cursul de la facturare și cel de la încasare e o diferență de curs valutar (venit/cheltuială financiară), nu o corecție a bazei de TVA.
- **Ai și două alternative legale la cursul BNR:** cursul BCE sau cursul băncii prin care se face decontarea. Alegerea se aplică consecvent, nu se schimbă de la o factură la alta ca să iasă mai bine.

## Un exemplu

::: ghid-exemplu
**Factură de 1.000 EUR, faptul generator pe 15 mai.**

BNR a comunicat pe **14 mai** un curs de **4,9700 lei/EUR**, valabil pentru operațiunile din 15 mai. Acesta e cursul de folosit — nu cursul din 15 mai (care e valabil pentru 16 mai) și nu cel din ziua încasării.

- Baza de impozitare: 1.000 × 4,9700 = **4.970,00 lei**
- TVA 21%: **1.043,70 lei**

Dacă încasezi pe 10 iunie, la un curs de 5,0100 lei/EUR, diferența de 40 de lei (1.000 × 0,04) e o **diferență de curs valutar**, înregistrată ca venit financiar — baza de TVA rămâne 4.970 lei, neatinsă.
:::

## Ce se greșește în practică

- **Se folosește cursul din ziua încasării.** Baza de TVA se fixează la exigibilitate; ce se întâmplă la plată e o diferență de curs, nu o rebazare.
- **Se ia cursul „din ziua facturii" ca fiind cel publicat chiar în acea zi.** Cursul publicat de BNR într-o zi e valabil pentru ziua *următoare*; pentru operațiunea de azi se folosește cursul de ieri.
- **Se recalculează TVA la regularizări.** O factură corect emisă nu-și schimbă baza în lei fiindcă s-a mișcat cursul.
- **Se amestecă sursele.** Dacă ai ales cursul BNR, îl folosești consecvent; nu treci pe cursul băncii doar la facturile unde e mai avantajos.

## Ce face iConta

La emiterea unei facturi în valută, iConta preia cursurile oficiale direct de la BNR (curs.bnr.ro) și le stochează local, apoi fixează pe factură cursul cel mai recent cu dată de valabilitate ≤ data operațiunii — adică exact „ultimul curs comunicat" din art. 290 alin. (2). Cursul se îngheață la emitere și nu se recalculează ulterior. Pentru valutele cotate la 100 de unități (HUF, JPY și altele), aplicația împarte automat la multiplicator, ca să nu iasă o bază de o sută de ori mai mare.

Ce rămâne al tău: alegerea sursei de curs (BNR / BCE / banca de decontare) și stabilirea corectă a datei faptului generator, de care atârnă ziua cursului.

Vezi și: [diferențele de curs valutar la închidere](/ghid/diferente-curs-valutar-inchidere) — ce se întâmplă cu soldurile în valută la sfârșitul lunii.

[iConta.eu](/)
