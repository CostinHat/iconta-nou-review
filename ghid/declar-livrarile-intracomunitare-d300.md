---
title: "Cum declar livrările intracomunitare în D300?"
description: Livrările de bunuri și prestările de servicii intracomunitare se derivă automat din facturile cu partener UE. Manual, prin „Rând manual D300”, rămân doar regularizările — iar orice încercare de a dubla o sumă deja derivată automat e blocată explicit.
published: 2026-09-23
modified: 2026-10-13
poarta: v1
---

# Cum declar livrările intracomunitare în D300?

Livrarea de bunuri sau prestarea de servicii către un partener din UE se declară, în cazul normal, automat — motorul D300 o derivă direct din factură. Manual, prin „Rând manual D300”, rămân doar regularizările ulterioare.

## Temeiul legal

::: ghid-temei
„Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri către o persoană impozabilă sau către o persoană juridică neimpozabilă care acționează ca atare în alt stat membru decât cel în care începe expedierea sau transportul bunurilor, care îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de autoritățile fiscale din alt stat membru [...]”
— Codul fiscal, art. 294 alin. (2) lit. a) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice.”
— Codul fiscal, art. 278 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Datele înscrise incorect într-un decont de taxă se pot corecta prin decontul unei perioade fiscale ulterioare și se vor înscrie la rândurile de regularizări.”
— Codul fiscal, art. 323 alin. (3) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce se derivă automat

Pentru facturile cu partener din UE („țara partenerului” în spațiul UE), motorul derivă automat:

- **livrare de bunuri către UE, cotă 0%** → rândul 1 (coloana Valoare);
- **prestare de servicii intracomunitare emisă** (dacă tipul din D390 e „P") → rândul 3 și rândul 3.1 (coloana Valoare).

## Rândul 1 e și în allow-list — dar doar ca excepție

Rândul 1 apare și în lista de rânduri acceptate manual în „Rând manual D300”. Asta nu înseamnă că se introduce în paralel cu derivarea automată: gardul anti-dublă-numărare al motorului respinge orice suprapunere. Există un test dedicat exact pentru acest caz: o livrare intracomunitară deja derivată automat pe rândul 1, plus o încercare de a introduce manual rândul 1 (coloana Valoare) → eroare („refuz”), cu mesaj care conține explicit „dublă numărare" (testele aplicației). Rândul 1 manual are sens doar ca fallback, când operațiunea n-a fost deloc captată automat.

## Ce e strict manual: regularizările

Rândurile **2** („Regularizări livrări intracomunitare scutite conform art. 294 alin. (2) lit. a) și d)") și **4** (regularizări prestări servicii intracomunitare) apar, în motorul D300, doar în formula de însumare a rândului 19 (total taxă colectată), niciodată ca țintă a unei atribuiri automate. Sunt 100% manuale — orice corecție ulterioară a unei livrări/prestări deja înregistrate trece pe aceste rânduri.

## Ce se greșește în practică

Se introduce manual rândul 1 sau rândul 3 pentru o livrare deja captată automat dintr-o factură cu partener UE — aplicația respinge cererea cu eroare de dublă numărare, confirmat printr-un test dedicat exact pe acest scenariu.

## Ce face iConta.eu

Motorul D300 derivă automat rândurile 1 și 3 din facturile cu partener din UE, folosind și clasificarea bun/serviciu din D390 pentru distincția livrare-bunuri vs. prestare-servicii. Panoul „Rând manual D300” acoperă regularizările (rândurile 2 și 4) și, ca excepție validată, introducerea manuală a rândurilor 1 și 3 doar când operațiunea nu a fost deloc derivată automat — cu gard explicit împotriva dublei numărări.

[iConta.eu](/)
