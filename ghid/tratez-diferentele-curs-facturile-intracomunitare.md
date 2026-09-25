---
title: "Cum tratez diferențele de curs la facturile intracomunitare?"
description: "Diferența de curs apare la decontarea unei datorii sau creanțe provenite dintr-o factură intracomunitară în valută, nu la înregistrarea inițială a facturii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez diferențele de curs la facturile intracomunitare?

O factură intracomunitară (achiziție sau livrare) exprimată în valută trece prin două momente diferite din punct de vedere al cursului valutar: **înregistrarea inițială**, la cursul BNR din ziua operațiunii, și **decontarea** ulterioară (plata sau încasarea), care poate avea loc la un curs diferit. Diferența de curs, cea care se înregistrează pe 665/765, apare la al doilea moment — decontare — nu la primul. Faptul că factura e intracomunitară nu schimbă acest mecanism: creanța sau datoria rezultată e un element monetar în valută, tratat identic indiferent dacă partenerul e din România sau din alt stat membru UE.

## Temeiul legal

::: ghid-temei
„319. - O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii.
322. - (1) Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial pe parcursul lunii sau față de cele la care sunt înregistrate în contabilitate trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli din diferențe de curs valutar."
— OMFP 1802/2014, Reglementările contabile, pct. 319 și pct. 322 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Aplicat la o factură intracomunitară:

- La **înregistrarea facturii** (recepția mărfii sau emiterea facturii de livrare), se folosește cursul BNR din ziua operațiunii — indiferent dacă achiziția e supusă taxării inverse pentru TVA sau nu, cursul folosit pentru contravaloarea în lei e cel de la data operațiunii.
- Creanța (la livrare) sau datoria (la achiziție) rezultată rămâne, până la decontare, un **element monetar în valută** — nimic din natura intracomunitară a tranzacției nu schimbă acest tratament.
- La **decontare** (plata furnizorului sau încasarea de la client), dacă a intervenit un curs diferit față de cel din evidență, diferența se recunoaște ca venit (765) sau cheltuială (665) din diferențe de curs, în luna în care are loc decontarea.

## Ce se greșește în practică

- Se caută diferența de curs chiar la înregistrarea facturii intracomunitare, confundând cursul folosit pentru înregistrarea inițială cu o diferență de curs — la acest moment nu există încă nicio diferență, doar o conversie.
- Se presupune, greșit, că regimul de TVA al achiziției intracomunitare (taxare inversă) influențează cumva tratamentul contabil al diferenței de curs de la decontare — cele două sunt complet independente.
- Se omite reevaluarea datoriei/creanței intracomunitare rămase neachitate la finalul lunii, tratând-o ca și cum ar fi „în așteptare" fără sold de reevaluat.

## Ce face iConta.eu

Partea de **decontare** a unei datorii sau creanțe provenite dintr-o factură intracomunitară (indiferent dacă tranzacția de bază a fost o achiziție sau o livrare intracomunitară) trece prin același motor din iConta.eu folosit pentru orice decontare în valută: contabilul introduce tipul (creanță/datorie), suma în valută, cursul din evidență, iar aplicația calculează automat diferența 665/765 față de cursul BNR al zilei de decontare. Aplicația nu distinge, la acest pas, dacă factura de bază a fost intracomunitară sau internă — motorul lucrează generic cu creanța/datoria rezultată.

Ce nu acoperă acest circuit: cursul folosit la **înregistrarea inițială** a facturii intracomunitare (la recepție/emitere) nu ține de acest motor, ci de fluxul de facturare/achiziție separat. De asemenea, ecranul de decontare nu are un câmp pentru contul de bancă/casierie folosit efectiv — orice decontare introdusă din acest ecran se înregistrează implicit pe contul de bancă în valută standard, indiferent de contul real prin care a avut loc plata sau încasarea.

[iConta.eu](/)
