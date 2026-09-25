---
title: "Cum se declară în D390 o factură în euro?"
description: "Regula de conversie valutară pentru operațiunile intracomunitare declarate în D390 și cum tratează iConta.eu o factură fără curs de schimb completat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se declară în D390 o factură în euro?

D390 se completează exclusiv în lei. O factură emisă sau primită într-o operațiune intracomunitară, exprimată în euro sau în altă valută, trebuie convertită la cursul de schimb valabil la data exigibilității taxei — nu la cursul din ziua în care contabilul introduce datele în aplicație.

## Temeiul legal

::: ghid-temei
„(2) Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operaţiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Naţională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, valabil la data la care intervine exigibilitatea taxei pentru operaţiunea în cauză [...]. În contractele încheiate între părţi trebuie menţionat dacă pentru decontări va fi utilizat cursul de schimb al unei bănci comerciale, în caz contrar aplicându-se cursul de schimb comunicat de Banca Naţională a României sau cursul de schimb publicat de Banca Centrală Europeană."
— Codul fiscal (Legea 227/2015), art. 290 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă practic trei reguli:

- cursul de referință e, implicit, ultimul curs BNR sau ultimul curs BCE valabil la data exigibilității taxei operațiunii — nu cursul zilei facturii, dacă exigibilitatea intervine mai târziu;
- dacă părțile au convenit contractual un curs bancar comercial pentru decontare, acela se folosește — dar convenția trebuie să fie scrisă în contract;
- în lipsa unei asemenea mențiuni contractuale, se aplică automat cursul BNR sau BCE.

## Ce se greșește în practică

- Se introduce în evidență doar valoarea în valută a facturii, fără cursul de schimb folosit, presupunând că „se calculează automat" undeva mai târziu.
- Se folosește cursul din ziua emiterii facturii, chiar și atunci când exigibilitatea taxei intervine în altă zi (de exemplu la achizițiile intracomunitare, unde exigibilitatea nu coincide întotdeauna cu data facturii).
- Se ignoră cerința contractuală: dacă în contract nu apare explicit un curs bancar comercial, aplicarea acestuia (în loc de cursul BNR/BCE) e nefondată.

## Ce face iConta.eu

Baza operațiunilor intracomunitare pentru D390 se calculează în lei din valoarea totală minus TVA a facturii, sau, pentru facturile în valută, din valoare × curs. Dacă o factură e emisă sau primită în valută și **nu are cursul BNR completat pe document**, aplicația nu o convertește tacit și nu o include implicit ca și cum ar fi în lei — o **exclude** din calculul D390 și afișează un diagnostic explicit: „factură în valută fără curs BNR — exclusă din D390 (nu se poate exprima în lei); completează cursul pe factură".

Practic, dacă o factură IC în euro lipsește din declarația D390 generată, primul lucru de verificat e dacă are cursul de schimb completat pe document — nu presupunerea că operațiunea a fost omisă din alt motiv.

[iConta.eu](/)
