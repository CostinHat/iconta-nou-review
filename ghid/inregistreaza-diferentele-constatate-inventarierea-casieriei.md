---
title: "Cum se înregistrează diferențele constatate la inventarierea casieriei?"
description: "Ce spune norma despre inventarierea numerarului la final de an și de ce, în iConta.eu, diferențele de casierie nu se înregistrează prin ecranul de inventariere anuală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează diferențele constatate la inventarierea casieriei?

Numerarul din casierie intră, ca orice alt element de activ, sub obligația generală de inventariere anuală — dar are un termen și o modalitate de verificare specifice.

## Temeiul legal

::: ghid-temei
"Disponibilitățile în lei și în valută din casieria entității se inventariază în ultima zi
lucrătoare a exercițiului financiar, după înregistrarea tuturor operațiunilor de încasări și
plăți privind exercițiul respectiv, confruntându-se soldurile din registrul de casă cu
monetarul și cu cele din contabilitate." — OMFP 2861/2009, Anexa 1, pct. 29 alin. (3)
:::

Regula generală a inventarierii anuale rămâne cea din Legea contabilității nr. 82/1991, art. 7 alin. (1): obligația se aplică tuturor elementelor de active, datorii și capitaluri proprii, cel puțin o dată pe exercițiu financiar. Pentru casierie, norma cere explicit ca operațiunea să se facă în **ultima zi lucrătoare** a anului și abia **după** ce toate încasările și plățile aferente exercițiului au fost înregistrate — altfel comparația monetar/registru de casă/contabilitate nu are sens.

Norma nu detaliază, la pct. 29, cursul de schimb care trebuie folosit pentru evaluarea disponibilului în valută la data inventarierii — este o regulă de evaluare contabilă generală, nu o prevedere specifică inventarierii casieriei, și nu am identificat un text dedicat pe acest subiect.

## Ce se greșește în practică

- Se inventariază casieria înainte de a închide toate operațiunile de încasări/plăți ale exercițiului, ceea ce falsifică soldul de comparat.
- Se face confuzia dintre inventarierea casieriei (numerar efectiv) și inventarierea generală a stocurilor sau mijloacelor fixe — sunt operațiuni distincte, cu obiect diferit.
- Se așteaptă ca diferențele de casierie să fie înregistrate prin același ecran/operațiune folosită pentru plusuri și minusuri de stoc sau mijloace fixe.

## Ce face iConta.eu

Aici trebuie spus onest: ecranul "Inventariere anuală" din iConta.eu (operația `nota-inventariere`) acceptă doar patru tipuri de operațiuni — Plus stoc, Plus mijloc fix, Minus și Casare — iar pentru Plus/Minus contul de stoc trebuie să fie unul dintre cele șase acceptate explicit de aplicație: 371, 301, 302, 303, 345 sau 381. Contul de casierie (5311/5314) nu se regăsește printre acestea, iar aplicația refuză orice alt cont de stoc introdus.

Cu alte cuvinte, **diferențele constatate la inventarierea casieriei nu pot fi înregistrate prin ecranul de inventariere anuală din iConta.eu** — acesta este construit pentru stocuri și mijloace fixe, nu pentru numerar. Înregistrarea contabilă a plusului sau minusului de casă trebuie făcută separat, printr-o notă contabilă manuală.

[iConta.eu](/)
