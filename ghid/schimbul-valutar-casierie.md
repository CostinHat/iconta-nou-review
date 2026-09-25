---
title: "Cum se face schimbul valutar la casierie"
description: "Cum se înregistrează contabil o sumă în valută aflată în casieria firmei, la cursul BNR — și diferența față de operațiunea unei case de schimb valutar autorizate."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se face schimbul valutar la casierie

O firmă obișnuită nu poate face „schimb valutar" în sensul unei case de schimb — cumpărarea și vânzarea de valută e o activitate licențiată separat. Ce poate face, și face frecvent, e să încaseze sau să dețină numerar în valută la propria casierie și să-l convertească în lei prin bancă. Contabilizarea acestei operațiuni urmează regulile de curs valutar din OMFP 1802/2014.

## Temeiul legal

::: ghid-temei
„La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate se recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz."
— OMFP 1802/2014, pct. 325 alin. (1) (sursă: anaf_surse/omfp_1802_2014.txt)
:::

Ce rezultă pentru numerarul în valută aflat în casierie:

- **Regula de bază**: disponibilitățile (inclusiv numerarul) în valută se reevaluează, la finalul fiecărei luni, la cursul BNR din ultima zi bancară a lunii — nu se lasă la cursul de la data încasării inițiale (pct. 325).
- **Diferențele de curs la decontare** (când suma în valută intră sau iese efectiv din casierie, la un curs diferit de cel la care era înregistrată) se recunosc imediat, în luna în care apar, ca venituri sau cheltuieli financiare (OMFP 1802/2014 pct. 322).
- **Conversia efectivă în lei** a numerarului în valută — adică schimbul propriu-zis — se face printr-o bancă sau printr-o casă de schimb valutar autorizată, nu prin firmă însăși: cumpărarea/vânzarea de valută, ca activitate, e licențiată separat (reglementată de BNR), diferit de simpla deținere și evidențiere contabilă a numerarului în valută încasat din activitatea curentă a firmei.
- **Cursul folosit la facturare** rămâne cel din Codul fiscal art. 290 alin. (2): ultimul curs BNR comunicat, valabil la data exigibilității taxei — un reper diferit de reevaluarea lunară a soldurilor, aplicabil la momentul emiterii facturii, nu la finalul lunii.

## Ce se greșește în practică

- Se confundă reevaluarea lunară a soldurilor în valută (pct. 325, aplicabilă disponibilităților existente) cu recunoașterea diferenței de curs la decontare (pct. 322, aplicabilă doar când suma chiar se încasează/plătește) — sunt momente diferite, cu reguli similare, dar nu identice.
- Se presupune că firma poate face „schimb valutar" ca activitate proprie (cumpărare/vânzare de valută pentru profit din diferența de curs) — activitate rezervată caselor de schimb valutar autorizate, nu unei firme obișnuite care doar deține numerar în valută din activitatea sa curentă.
- Se lasă numerarul în valută neevaluat luni de zile, fără reevaluare la cursul BNR, ceea ce denaturează soldul contabil și rezultatul financiar aferent diferențelor de curs.

## Ce face iConta.eu

Funcționalitatea **Curs valutar BNR** furnizează cursul oficial pentru orice operațiune în valută — pentru facturare (art. 290 CF) sau pentru decontări/reevaluări (OMFP 1802/2014). Modulul de casierie tratează separat numerarul în valută (contul 5314, față de 5311 pentru lei) și avansurile de trezorerie acordate/restituite în valută, iar aplicația oferă operațiuni dedicate de „Reevaluare lunară solduri valută" și „Decontare în valută", care calculează diferența de curs (665/765) conform pct. 322/325 din OMFP 1802/2014.

Aplicația **nu are** un ecran dedicat operațiunii de „schimb valutar" propriu-zise (adică conversia numerarului în valută în lei, la o bancă sau casă de schimb) — nu s-a găsit nicio funcție care să înregistreze automat această conversie. Contabilul folosește operațiunile existente de reevaluare/decontare, introducând manual cursul de la schimb ca „curs de decontare".

[iConta.eu](/)
