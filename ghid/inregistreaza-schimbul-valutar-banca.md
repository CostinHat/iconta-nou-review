---
title: "Cum se înregistrează schimbul valutar făcut prin bancă?"
description: "Cum se contează o operațiune de schimb valutar derulată prin bancă, la ce curs se înregistrează și cum apar diferențele de curs."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează schimbul valutar făcut prin bancă?

Un schimb valutar prin bancă (de exemplu, conversia unei încasări în euro pentru plata unei facturi în lei, sau invers) nu e o simplă mișcare de disponibilități — implică două monede, două cursuri diferite (cel de la data operațiunii de schimb și cel de evidență contabilă anterior) și, aproape întotdeauna, o diferență de curs valutar de înregistrat.

## Temeiul legal

::: ghid-temei
„O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii."
— OMFP 1802/2014 (reglementări contabile), pct. 319 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Regula de bază e simplă — cursul folosit e cursul BNR din ziua operațiunii, nu cursul băncii comerciale la care s-a făcut efectiv schimbul (acesta din urmă generează, dacă diferă de cursul BNR, o diferență de curs sau un cost de schimb, tratat separat, nu ca eroare de înregistrare). Pentru operațiunea de schimb valutar propriu-zisă:

- **Se înregistrează ieșirea din contul valutar** la cursul de evidență anterior al sumei respective (cursul la care a fost înregistrată inițial acea sumă în contabilitate).
- **Se înregistrează intrarea în contul în lei** la cursul BNR din ziua operațiunii de schimb.
- **Diferența dintre cele două valori** (dacă suma în valută avea deja un curs de evidență diferit de cel din ziua schimbului) se recunoaște ca diferență de curs valutar favorabilă (cont 765) sau nefavorabilă (cont 665), în luna în care are loc operațiunea.
- **Comisionul băncii pentru operațiunea de schimb** se înregistrează separat, ca și cheltuială cu serviciile bancare (cont 627), distinct de diferența de curs valutar.

## Ce se greșește în practică

- Se folosește cursul de schimb efectiv aplicat de bancă (care include marja băncii) ca și curs contabil, în loc de cursul BNR din ziua operațiunii — diferența dintre cele două e, corect, un cost bancar, nu o reevaluare valutară.
- Se omite recunoașterea diferenței de curs valutar între cursul de evidență al sumei în valută și cursul BNR din ziua schimbului, tratând operațiunea doar ca o simplă mutare de disponibilități.
- Se amestecă diferența de curs valutar cu comisionul bancar de schimb, deși sunt două elemente contabile distincte, cu conturi diferite.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă un modul dedicat de calcul al diferențelor de curs valutar (665/765), inclusiv nota de decontare pentru operațiunile de schimb și reevaluarea soldurilor în valută la cursul BNR de sfârșit de lună — funcționalitate reală, folosită automat la contabilizarea extraselor bancare cu operațiuni valutare.

[iConta.eu](/)
