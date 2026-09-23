---
title: Cum se calculează amortizarea degresivă?
description: Amortizarea degresivă multiplică cota liniară cu un coeficient (1,5, 2,0 sau 2,5, în funcție de durata activului) și se aplică pe valoarea rămasă, cu trecere obligatorie la metoda liniară în anul în care aceasta devine mai avantajoasă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează amortizarea degresivă?

Amortizarea degresivă pornește de la cota liniară, dar o multiplică cu un coeficient legal, aplicat pe valoarea **rămasă** de amortizat (nu pe valoarea inițială) — ceea ce produce cheltuieli mai mari în primii ani și mai mici spre final, cu o regulă de comutare obligatorie la metoda liniară la un moment dat.

## Temeiul legal

::: ghid-temei
[...] amortizarea se calculează prin multiplicarea cotelor de amortizare liniară cu unul dintre coeficienții următori: a) 1,5, dacă durata normală de utilizare a mijlocului fix amortizabil este între 2 și 5 ani; [...] b) 2,0, dacă durata normală de utilizare... este între 6 și 10 ani; [...] c) 2,5, dacă durata normală de utilizare... este mai mare de 10 ani.

— Codul fiscal (Legea 227/2015), art.28 alin.(7)
:::

Coeficientul depinde exclusiv de durata normală de funcționare aleasă pentru activ: 1,5 pentru active cu durată de 2-5 ani, 2,0 pentru 6-10 ani, 2,5 pentru peste 10 ani. Cota degresivă anuală (cotă liniară × coeficient) se aplică pe valoarea **rămasă** de amortizat, nu pe valoarea inițială — de aici scăderea treptată a sumei de la un an la altul. Regula obligatorie de trecere la liniar: din anul în care amortizarea liniară calculată pe valoarea și durata rămase ar fi **mai mare** decât cea degresivă, se trece definitiv la liniar pentru anii rămași.

**Exemplu numeric**: același echipament tehnologic, valoare fiscală **24.000 lei**, durată **4 ani** (încadrată în plaja 2-5 ani → coeficient 1,5).

- cotă liniară = 25%; cotă degresivă = 25% × 1,5 = **37,5%**;
- **anul 1**: 24.000 × 37,5% = **9.000 lei**; valoare rămasă = 15.000 lei;
- **anul 2**: se compară degresivul pe valoarea rămasă (15.000 × 37,5% = 5.625 lei) cu liniarul pe valoarea și durata rămase (15.000 / 3 ani = 5.000 lei) — degresivul (5.625) e mai mare, rămâne degresiv → **5.625 lei**; valoare rămasă = 9.375 lei;
- **anul 3**: degresiv pe rest (9.375 × 37,5% = 3.515,625 lei) vs. liniar pe rest (9.375 / 2 ani = 4.687,5 lei) — acum liniarul e mai mare, se trece la liniar → **4.687,5 lei**;
- **anul 4**: rămâne liniar → **4.687,5 lei**;
- total: 9.000 + 5.625 + 4.687,5 + 4.687,5 = **24.000 lei**, exact valoarea de intrare, integral recuperată.

## Ce se greșește în practică

- Se aplică cota degresivă pe valoarea inițială de intrare în fiecare an, în loc de valoarea rămasă — greșeala produce o amortizare mult mai mare decât cea legală.
- Se uită trecerea la metoda liniară în anul în care aceasta devine mai avantajoasă, continuând degresivul până la epuizarea artificială a valorii, ceea ce nu corespunde formulei legale.
- Se aplică degresivul unei categorii de active care nu-l permite (de exemplu, construcțiilor, unde legea impune exclusiv metoda liniară).

## Ce face iConta.eu

Amortizarea degresivă e implementată exact conform mecanismului legal: cota liniară multiplicată cu coeficientul corespunzător duratei (1,5 / 2,0 / 2,5), aplicată pe valoarea rămasă, cu comutare automată la liniar din anul în care aceasta devine mai avantajoasă — calculul e identic în registrul mijloacelor fixe, nota lunară de amortizare, D406/SAF-T, casare și reevaluare. Dacă alegeți metoda degresivă pentru o categorie de active care n-o permite (de exemplu, construcții), aplicația nu calculează tacit o cifră liniară în loc — rândul respectiv arată eroare, până corectați metoda.

[iConta.eu](/)
