---
title: Ce fac cu o diferență de TVA semnalată de sistem
description: Un roșu afișat de aplicație pe unul din conturile de TVA vine dintr-o comparație internă D300-balanță, nu de la ANAF — următorul pas depinde de dacă diferența are o cauză dovedită mecanic sau cere investigație.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce fac cu o diferență de TVA semnalată de sistem

Când aplicația marchează cu roșu unul din conturile de TVA, semnalul vine dintr-o comparație internă — D300 vs balanța contabilă — și nu dintr-un canal extern (ANAF). Ce faci mai departe depinde de tipul cauzei pe care sistemul o poate identifica.

## Temeiul legal

::: ghid-temei
Art. 281 din Codul fiscal (Legea 227/2015) — "Faptul generator pentru livrări de bunuri și prestări de servicii" — stabilește momentul de la care se naște obligația de TVA. D300 se calculează pe facturile lunii; balanța pe înregistrările contabile efectiv făcute — comparația internă a aplicației se bazează pe acest temei. Titlul și numărul articolului sunt confirmate în sursele legale folosite de aplicație; textul integral nu e citat literal aici.
:::

## Cele trei tipuri de cauză

- **Executabilă** — diferența e explicată exact de o factură (emisă sau primită) fără notă contabilă validată. Aplicația poate propune corecția, care rămâne totuși ca notă de validat (principiul celor patru ochi), nu se aplică automat fără confirmare.
- **Sugerată** — există deja o notă în ciornă care ar rezolva diferența, dar nu a fost încă validată. Acțiunea aici e să validezi nota, nu să creezi una nouă.
- **De investigație** — cauza nu poate fi dovedită mecanic din date: note manuale introduse direct pe cont, storno neînregistrat, TVA la încasare (exigibilitate decalată), regularizări, sau facturi înregistrate în altă lună decât cea a documentului. Aici aplicația nu ajustează nimic automat — verifici manual documentele care ar putea explica diferența.

## Cum interpretezi starea

- **roșu** — diferență reală, peste toleranța de 1 leu, cu cifrele afișate.
- **gri** — nu s-a putut verifica (de regulă lipsesc date necesare comparației) — nu înseamnă „e în regulă", ci „nu am destule informații".
- **verde** — sumele coincid, dar poate fi fals-pozitiv dacă lipsesc simetric facturi din ambii termeni ai comparației; sistemul degradează atunci starea la gri, tocmai pentru a nu induce o falsă asigurare.

## Ce se greșește în practică

- Se validează în grabă o corecție propusă, fără să se verifice dacă e cu adevărat cauza exactă a diferenței sau doar o coincidență valorică.
- Se ignoră un gri, tratându-l ca pe un verde — gri înseamnă că sistemul nu a putut trage o concluzie, nu că totul e corect.
- Se caută diferența doar în facturi noi, ignorând posibilitatea unui storno neînregistrat sau a unei note manuale introduse direct pe cont, în lunile anterioare.

## Ce face iConta.eu

Aplicația rulează automat comparația D300–balanță pe conturile de TVA (4427, 4426, 4423, 4424, informativ 4428), pe bază de note validate, cu toleranță de 1 leu, și clasifică fiecare diferență ca executabilă, sugerată sau de investigație. Pentru cauzele dovedite mecanic, propune corecția spre validare; pentru celelalte, semnalează situația fără să ajusteze automat contul.

[iConta.eu](/)
