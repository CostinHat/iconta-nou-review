---
title: "Cum contabilizez plata unei facturi în euro dintr-un cont în lei?"
description: "Explică ce curs BNR se folosește pentru o factură în euro și cum îl determină automat iConta.eu la emitere."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum contabilizez plata unei facturi în euro dintr-un cont în lei?

Punctul de plecare pentru orice factură în valută e stabilirea corectă a cursului la care se convertesc sumele în lei — plata efectivă dintr-un cont în lei nu schimbă regula, doar o pune în practică.

## Temeiul legal

::: ghid-temei
„Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României sau ultimul curs de schimb publicat de Banca Centrală Europeană ori cursul de schimb utilizat de banca prin care se efectuează decontările, valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză [...]”
— Codul fiscal (Legea 227/2015), art. 290 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii.”
— OMFP 1802/2014, pct. 319 (sursă: [OMFP nr. 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate)](https://legislatie.just.ro/Public/DetaliiDocument/164320))

„Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar.”
— OMFP 1802/2014, pct. 322 alin. (1) (sursă: [OMFP nr. 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate)](https://legislatie.just.ro/Public/DetaliiDocument/164320))
:::

Factura emisă în euro se înregistrează în lei la cursul BNR valabil la data operațiunii (de regulă data exigibilității taxei). Plata ulterioară, dintr-un cont în lei, nu recalculează acest curs — factura rămâne înregistrată la cursul ei propriu; diferența dintre cursul facturii și cursul zilei plății generează, contabil, o diferență de curs valutar la decontare (venit sau cheltuială financiară), tratată separat de cursul de TVA al facturii.

## Ce se greșește în practică

Greșeala frecventă e recalcularea bazei de TVA a facturii la cursul zilei plății, în loc să rămână la cursul de la emitere — cursul facturii e fix, doar decontarea (plata) generează eventual o diferență de curs separată. O altă greșeală e ignorarea completă a diferenței de curs dintre data facturii și data plății.

## Ce face iConta.eu

La emiterea unei facturi în euro, iConta.eu preia automat cursul BNR valabil la data facturii (motorul de curs) și îl atașează facturii; acest curs e folosit pentru toate conversiile ulterioare (D300, D390, D394, D406, contare), fără să fie recalculat la stornare sau la plată — la stornare se păstrează cursul facturii originale, nu cursul zilei de stornare. O factură în valută fără curs BNR asociat e exclusă automat din declarații (nu se ghicește un curs implicit de 1). Contabilul poate introduce și un curs manual, cu data comunicării lui — dar data cursului manual nu poate fi ulterioară datei facturii.

De reținut: data folosită de motor pentru cursul facturii e data emiterii facturii, nu neapărat o dată separată de exigibilitate a taxei — pentru majoritatea operațiunilor cele două coincid, dar pot diferi (de exemplu la avansuri sau facturare întârziată), caz în care verificarea manuală a cursului corect rămâne în sarcina contabilului.

[iConta.eu](/)
