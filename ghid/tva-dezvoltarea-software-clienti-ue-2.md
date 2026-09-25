---
title: "TVA pentru dezvoltarea de software către clienți din UE"
description: "Regula generală privind locul prestării serviciilor B2B din Codul fiscal, aplicată serviciilor de dezvoltare software facturate unor clienți impozabili din alte state UE."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# TVA pentru dezvoltarea de software către clienți din UE

Un serviciu de dezvoltare software facturat unei firme dintr-un alt stat membru UE nu are o regulă specială de TVA — el urmează regula generală aplicabilă serviciilor B2B, care mută locul prestării la sediul beneficiarului.

## Temeiul legal

::: ghid-temei
„Locul de prestare a serviciilor către o persoană impozabilă care acționează ca atare este locul unde respectiva persoană care primește serviciile își are stabilit sediul activității sale economice. Dacă serviciile sunt furnizate către un sediu fix al persoanei impozabile, aflat în alt loc decât cel în care persoana își are sediul activității sale economice, locul de prestare a serviciilor este locul unde se află respectivul sediu fix al persoanei care primește serviciile. În absența unui astfel de loc sau sediu fix, locul de prestare a serviciilor este locul unde persoana impozabilă care primește aceste servicii își are domiciliul stabil sau reședința obișnuită."
— Cod fiscal, art. 278 alin. (2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Aplicat unei firme românești care dezvoltă software pentru un client impozabil dintr-un alt stat UE:

- Locul prestării serviciului e considerat **statul membru unde clientul are sediul activității economice** — nu România. Prestatorul român facturează fără TVA, cu mențiunea corespunzătoare (operațiune neimpozabilă în România, taxare inversă la beneficiar).
- Această regulă se aplică indiferent dacă serviciul e "produs" tehnic în România — locul prestării, în sensul TVA, nu e legat de locul unde se desfășoară efectiv munca de dezvoltare, ci de sediul beneficiarului.
- Operațiunea trebuie raportată în **declarația recapitulativă** (VIES) de către prestator, potrivit art. 325 alin. (1) lit. c) din Codul fiscal — care menționează explicit "prestările de servicii prevăzute la art. 278 alin. (2) efectuate în beneficiul unor persoane impozabile nestabilite în România, dar stabilite în Uniunea Europeană".
- Dacă beneficiarul e o persoană **neimpozabilă** (persoană fizică fără activitate economică, chiar dintr-un alt stat UE), regula se schimbă: locul prestării rămâne la sediul prestatorului (art. 278 alin. (3)), iar factura se emite cu TVA românească.

## Ce se greșește în practică

- Se aplică taxare inversă și pentru clienți persoane fizice fără activitate economică din alt stat UE, confundând regula pentru beneficiar persoană impozabilă (alin. 2) cu cea pentru beneficiar neimpozabil (alin. 3).
- Se omite raportarea în declarația recapitulativă (D390) a serviciilor de dezvoltare software facturate fără TVA către un client impozabil din UE, tratând operațiunea doar ca pe o factură obișnuită de export de servicii.
- Se presupune că verificarea codului valid de TVA al clientului nu e necesară — validarea calității de persoană impozabilă (de exemplu prin sistemul VIES) rămâne un pas practic esențial pentru a justifica aplicarea corectă a regulii B2B.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează facturile pentru clienți din UE și declarația recapitulativă (D390), dar nu are o funcție specifică dedicată serviciilor de dezvoltare software — încadrarea corectă a locului prestării, în funcție de calitatea beneficiarului, rămâne o verificare a contabilului la emiterea facturii.

[iConta.eu](/)
