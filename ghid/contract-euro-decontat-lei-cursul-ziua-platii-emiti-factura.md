---
title: "Contract în euro decontat în lei la cursul din ziua plății: emiți factură pentru diferența de curs?"
description: "Nu. La livrările interne contractate în valută și decontate în lei la cursul zilei plății, diferența de curs nu e diferență de preț, nu se facturează și nu modifică TVA."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Contract în euro decontat în lei la cursul din ziua plății: emiți factură pentru diferența de curs?

Nu. Dacă o livrare sau o prestare în interiorul țării e contractată în euro, cu plata în lei la cursul din ziua plății, diferența dintre cursul din factură și cursul de la încasare nu este diferență de preț. Nu se emite factură pentru ea și nu se modifică TVA.

Diferența se înregistrează doar contabil, ca venit sau cheltuială financiară. Baza de TVA și TVA colectată rămân cele din factura inițială, la cursul valabil la data exigibilității.

## Temeiul legal

::: ghid-temei
„Pentru livrări de bunuri sau prestări de servicii în interiorul țării, contractate în valută cu decontare în lei la cursul de schimb din data plății, diferențele de curs dintre cursul de schimb menționat în factura întocmită conform alin. (1) și cursul de schimb utilizat la data încasării nu sunt considerate diferențe de preț și nu se emite o factură în acest sens."
— HG 1/2016 (Normele Codului fiscal), titlul VII, pct. 35 alin. (3) (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

::: ghid-temei
„Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză"
— Codul fiscal (Legea 227/2015), art. 290 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

::: ghid-temei
„b) Pentru creanțele și datoriile, exprimate în lei, a căror decontare se face în funcție de cursul unei valute, eventualele diferențe favorabile sau nefavorabile, care rezultă din evaluarea acestora se înregistrează la alte venituri sau alte cheltuieli financiare, după caz."
— OMFP 1802/2014 (reglementările contabile), pct. 94 lit. b) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce înseamnă concret:

- **Baza de TVA** se stabilește o singură dată, la cursul valabil la data exigibilității taxei (art. 290 alin. (2)). Ulterior nu se mai recalculează pentru mișcarea cursului.
- **Diferența de la încasare** e un rezultat financiar, nu o corecție de preț. Nu apare pe nicio factură și nu intră în decontul de TVA.
- **Contul.** Creanța facturată în lei, cu decontare în funcție de cursul euro, e o creanță în lei. Diferențele ei merg la alte venituri sau cheltuieli financiare (768 sau 668), potrivit pct. 94 lit. b) din OMFP 1802/2014. Conturile 765 și 665 sunt pentru creanțele și datoriile ținute în valută.
- **Cursul aplicabil** poate fi ultimul curs BNR, ultimul curs BCE sau cursul băncii prin care se efectuează decontările, valabil la data exigibilității (art. 290 alin. (2)).
- Regula privește operațiunile **în interiorul țării**. Achizițiile și livrările intracomunitare au reguli proprii de curs (pct. 35 alin. (4) și (5)).

::: ghid-exemplu
SC Exemplu SRL facturează unui client din România servicii de 1.000 euro + TVA 21%. Contractul prevede plata în lei la cursul BNR din ziua plății.

- Factura, la cursul de 5,00 lei/euro: bază 5.000 lei, TVA 1.050 lei, total 6.050 lei. Nota: 4111 = 704 cu 5.000 lei și 4111 = 4427 cu 1.050 lei.
- Încasarea: clientul plătește 1.210 euro la cursul de 5,05 lei/euro, adică 6.110,50 lei.
- Diferența de 60,50 lei: 5121 = 4111 cu 6.050 lei și 5121 = 768 cu 60,50 lei.

Nu se emite factură pentru cei 60,50 lei. TVA colectată rămâne 1.050 lei.
:::

## Ce se greșește în practică

- Se emite o factură „de diferență de curs", cu TVA. Normele spun că nu e diferență de preț și că nu se emite factură.
- Se recalculează TVA la cursul din ziua încasării. Cursul relevant pentru TVA e cel de la exigibilitate.
- Se folosește cursul unei bănci comerciale prin care nu se efectuează decontările operațiunii.
- Diferența se înregistrează pe 704 sau 628, ca și cum ar fi o corecție de preț, în loc de un cont de venituri sau cheltuieli financiare.

## Ce face iConta.eu

iConta.eu preia cursul BNR și îl aplică facturilor în valută, după regula cursului valabil la data operațiunii, inclusiv pentru conversia TVA. Pentru creanțele și datoriile ținute în valută, calculează automat diferența de curs la încasare sau plată și o înregistrează pe 765 sau 665. Pentru o creanță în lei cu decontare la cursul euro, aplicația nu are o regulă dedicată pe 768 sau 668. Diferența se înregistrează prin notă contabilă în Registrul jurnal, validată de contabil. Factura inițială și TVA din ea nu se modifică.

[iConta.eu](/)
