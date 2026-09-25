---
title: "TVA pentru serviciile de publicitate online prestate intra-UE"
description: "Unde se taxează, din perspectiva TVA, un serviciu de publicitate online facturat unei firme dintr-un alt stat membru UE."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA pentru serviciile de publicitate online prestate intra-UE

O firmă românească ce prestează servicii de publicitate online (campanii, gestionare de reclame, consultanță de marketing digital) pentru un client persoană impozabilă dintr-un alt stat membru UE trebuie să stabilească, întâi de toate, unde are loc, fiscal, prestarea — pentru că de asta depinde cine colectează TVA.

## Temeiul legal

::: ghid-temei
„(2) Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. Dacă serviciile sunt furnizate către un sediu fix al persoanei impozabile, aflat în alt loc decât cel în care persoana își are sediul activității sale economice, locul de prestare a serviciilor este locul unde se află respectivul sediu fix al persoanei care primește serviciile."
— Legea nr. 227/2015 (Codul fiscal), art. 278 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Regula de bază pentru serviciile B2B (între persoane impozabile) este simplă, dar produce des confuzie tocmai pentru că e diferită de regula pentru serviciile către persoane neimpozabile:

- Pentru servicii de publicitate online prestate către o **persoană impozabilă** dintr-un alt stat membru UE, locul prestării — și deci locul unde se datorează TVA — este **la sediul beneficiarului**, nu la sediul prestatorului.
- Consecința practică: prestatorul din România **nu colectează TVA românească** pe factură; beneficiarul din celălalt stat membru aplică taxare inversă (self-charge) în statul lui, conform echivalentului local al art. 307 alin. (2).
- Operațiunea se raportează în declarația recapitulativă (D390), la categoria prestărilor de servicii intracomunitare de la art. 278 alin. (2), pentru luna în care ia naștere exigibilitatea taxei.
- Excepțiile de la regula generală (art. 278 alin. (4)-(5), pentru servicii legate de bunuri imobile, transport de călători, restaurant etc.) nu se aplică, de regulă, serviciilor de publicitate online — acestea rămân sub regula generală B2B.

## Ce se greșește în practică

- Se aplică TVA românească pe factura către clientul UE, din prudență sau din necunoaștere a regulii, deși legea impune taxare la sediul beneficiarului, nu al prestatorului.
- Se omite raportarea operațiunii în declarația recapitulativă (D390), considerându-se că, „fiind fără TVA", nu trebuie declarată — obligația de raportare rămâne, indiferent că taxa nu apare pe factură.
- Se verifică valabilitatea codului de TVA al clientului din alt stat membru abia după emiterea facturii, sau deloc — fără acest cod valid, prestatorul nu poate justifica aplicarea regulii B2B și riscă recalificarea operațiunii.

## Ce face iConta.eu

Verificat în cod: modulul `core/d390.py` tratează explicit operațiunile de tip „achiziții servicii intracomunitare (art. 307 alin. (2) CF = servicii art. 278 alin. (2) de la prestator UE)" pentru raportarea în declarația recapitulativă, aplicând logica de taxare inversă pentru serviciile B2B intracomunitare. Aplicația reflectă corect încadrarea legală a acestor operațiuni în structura D390; verificarea codului de TVA al clientului din alt stat membru și corectitudinea facturării fără TVA rămân, ca de obicei, responsabilitatea contabilului la introducerea datelor.

[iConta.eu](/)
