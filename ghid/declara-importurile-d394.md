---
title: "Se declară importurile în D394?"
description: "De ce achizițiile de bunuri din afara UE nu apar în D394 și cum tratează iConta.eu, automat, achizițiile provenite de la parteneri non-UE."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Se declară importurile în D394?

D394 e o declarație despre operațiuni „pe teritoriul național" — iar importul de bunuri, prin natura lui, are un regim de TVA propriu, colectat de regulă în vamă, nu prin mecanismul de taxare inversă pe care D394 îl urmărește pentru achizițiile interne.

## Temeiul legal

::: ghid-temei
„Se vor declara numai operaţiunile taxabile pentru care locul livrării/prestării este în România conform art. 275, respectiv art. 278 din Codul fiscal şi, în cazul achiziţiilor de bunuri/servicii, beneficiarul este obligat la plata TVA conform art. 307 alin. (2), (3), (5) şi (6) din Codul fiscal. Nu vor fi declarate operaţiunile de export şi import de bunuri (inclusiv în cazul persoanei impozabile pentru care s-a acordat certificat de amânare de la plata în vamă a TVA), precum şi operaţiunile care se înscriu în declaraţia recapitulativă privind livrările/achiziţiile/prestările intracomunitare (formular 390)."
— OPANAF 2194/2025, Anexa 2, Cartuș F pct.10 (sursă: anaf_surse/opanaf_2194_2025_d394.txt:963-968)
:::

- Importul de bunuri, chiar și cel efectuat cu certificat de amânare de la plata TVA în vamă, nu se declară în D394 — regimul lui de TVA e altul (plată/amânare la vamă, nu taxare inversă raportată aici).
- Excluderea privește achizițiile „cu taxare inversă" de la parteneri neînregistrați/nestabiliți în UE — categoria în care s-ar putea încadra greșit un import de marfă. Legea o exclude explicit din acest cartuș.
- Regula se completează cu excluderea deja cunoscută a achizițiilor intracomunitare (D390) — practic, D394 raportează doar achizițiile interne, cu partener stabilit sau nu în România, nu și fluxurile transfrontaliere de bunuri.

## Ce se greșește în practică

- Se declară o achiziție de import ca operațiune cu taxare inversă (tip C), confundând-o cu achizițiile de bunuri/servicii de la parteneri stabiliți în UE care intră efectiv sub art.307.
- Se presupune, greșit, că regula simetrică se aplică și livrărilor: exporturile **sunt** declarate în D394 (ca livrare, cotă 0), spre deosebire de importuri, care nu sunt declarate deloc.
- Se amestecă certificatul de amânare de la plata TVA în vamă cu o scutire de declarare în altă parte — amânarea privește doar momentul plății TVA la import, nu obligația de declarare (care rămâne oricum în afara D394).

## Ce face iConta.eu

Clasificarea partenerului (`core/d394.py`, funcția `clasifica_partener()`) încadrează furnizorii/clienții după prefixul CUI: RO, fără CUI, țară UE sau țară non-UE. Pentru achizițiile de tip „primit" (direcția inversă livrării), generatorul exclude explicit din D394 orice operațiune cu partener din categoria UE sau non-UE — comentariul din cod spune direct „ACHIZIȚIILE INTRACOMUNITARE NU INTRĂ ÎN D394 — se declară în D390 (VIES)", iar aceeași excludere acoperă și achizițiile de la parteneri non-UE, categorie în care intră tipic importurile de bunuri. Parteneri din aceste categorii apar în D394 doar la livrări (export, tip L/LS) sau la achiziții de servicii cu taxare inversă conform art.307/331 — niciodată la achiziții de bunuri importate.

[iConta.eu](/)
