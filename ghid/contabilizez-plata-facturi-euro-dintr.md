---
title: "Cum contabilizez plata unei facturi în euro dintr-un cont în lei?"
description: "Explică ce curs BNR se folosește pentru o factură în euro și cum îl determină automat iConta.eu la emitere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum contabilizez plata unei facturi în euro dintr-un cont în lei?

Punctul de plecare pentru orice factură în valută e stabilirea corectă a cursului la care se convertesc sumele în lei — plata efectivă dintr-un cont în lei nu schimbă regula, doar o pune în practică.

## Temeiul legal

::: ghid-temei
"(2) Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri, se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României [...] valabil la data la care intervine exigibilitatea taxei pentru operațiunea în cauză [...]"
— Codul fiscal (Legea 227/2015), art. 290 alin. (2), `anaf_surse/cod_fiscal_227_2015_consolidat.txt:17959-17965`, dosar de cercetare F025.

"În sensul art. 290 alin. (2) din Codul fiscal, prin ultimul curs de schimb comunicat de Banca Națională a României se înțelege cursul de schimb comunicat de respectiva bancă în ziua anterioară și care este valabil pentru operațiunile care se vor desfășura în ziua următoare."
— HG 1/2016 (norme metodologice CF), pct. 35 alin. (1), `anaf_surse/hg_1_2016_norme_cod_fiscal.txt:6849-6851`, dosar de cercetare F025.
:::

Factura emisă în euro se înregistrează în lei la cursul BNR valabil la data operațiunii (de regulă data exigibilității taxei). Plata ulterioară, dintr-un cont în lei, nu recalculează acest curs — factura rămâne înregistrată la cursul ei propriu; diferența dintre cursul facturii și cursul zilei plății generează, contabil, o diferență de curs valutar la decontare (venit sau cheltuială financiară), tratată separat de cursul de TVA al facturii.

## Ce se greșește în practică

Greșeala frecventă e recalcularea bazei de TVA a facturii la cursul zilei plății, în loc să rămână la cursul de la emitere — cursul facturii e fix, doar decontarea (plata) generează eventual o diferență de curs separată. O altă greșeală e ignorarea completă a diferenței de curs dintre data facturii și data plății.

## Ce face iConta.eu

La emiterea unei facturi în euro, iConta.eu preia automat cursul BNR valabil la data facturii (`core/curs_bnr.py`, motorul de curs) și îl atașează facturii; acest curs e folosit pentru toate conversiile ulterioare (D300, D390, D394, D406, contare), fără să fie recalculat la stornare sau la plată — la stornare se păstrează cursul facturii originale, nu cursul zilei de stornare. O factură în valută fără curs BNR asociat e exclusă automat din declarații (nu se ghicește un curs implicit de 1). Contabilul poate introduce și un curs manual, cu data comunicării lui — dar data cursului manual nu poate fi ulterioară datei facturii.

De reținut: data folosită de motor pentru cursul facturii e data emiterii facturii, nu neapărat o dată separată de exigibilitate a taxei — pentru majoritatea operațiunilor cele două coincid, dar pot diferi (de exemplu la avansuri sau facturare întârziată), caz în care verificarea manuală a cursului corect rămâne în sarcina contabilului.

[iConta.eu](/)
