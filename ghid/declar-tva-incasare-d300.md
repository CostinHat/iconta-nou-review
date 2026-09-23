---
title: Cum declar TVA la încasare în D300?
description: TVA calculată prin sistemul de încasare nu are un rând separat în D300 — ajunge în rândurile obișnuite de TVA colectată (R9_1/R9_2, R10, R11), iar deducerea la beneficiar se amână prin bifa de la rândul B1, conform art. 297 Cod fiscal.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum declar TVA la încasare în D300?

Mulți contabili caută în formularul D300 un rând dedicat „TVA la încasare" — și nu îl găsesc, pentru că nu există. Regimul de încasare nu creează o categorie separată de raportare, ci doar schimbă momentul în care o sumă ajunge în decont.

## Temeiul legal

::: ghid-temei
**Art. 282 alin. (3) din Codul fiscal (Legea 227/2015)**: *„...exigibilitatea taxei intervine la data încasării contravalorii integrale sau parțiale a livrării de bunuri ori a prestării de servicii, în cazul persoanelor impozabile care optează în acest sens..."*

**Art. 297 alin. (2) CF**: *„Dreptul de deducere a TVA aferente achizițiilor efectuate de o persoană impozabilă de la o persoană impozabilă care aplică sistemul TVA la încasare... este amânat până la data la care taxa aferentă... a fost plătită furnizorului."*

Verificat direct în codul sursă (`static/js/ecrane/facturi_ecran.js`): `furnizor_tva_incasare: corp.querySelector("#pr-furnizor-incasare").checked, // [B1 D300]`.
:::

## Ce înseamnă practic

**Pe partea de vânzări**, când firma ta e înscrisă la TVA la încasare, sumele încasate/alocate pe facturile emise sunt trecute prin calculul de exigibilitate (sută mărită) pe fiecare cotă, iar rezultatul ajunge exact în rândurile obișnuite de TVA colectată — R9_1/R9_2 pentru 21%, R10 pentru 11%, R11 pentru cota tranzitorie de 9%. Nu există un rând separat pentru „TVA la încasare": suma pur și simplu apare în decont **în perioada în care a fost încasată**, nu în cea în care a fost facturată. Până atunci, TVA rămâne în contul 4428 (neexigibil), în afara decontului.

**Pe partea de achiziții**, dacă furnizorul tău aplică TVA la încasare, dreptul tău de deducere e amânat până plătești factura (art. 297 alin. (2)) — bifarea acestei situații pe factura de achiziție alimentează rândul B1 din D300, exact eticheta din cod (`[B1 D300]`).

## Ce se greșește în practică

- **Se caută un rând D300 dedicat „TVA la încasare".** Nu există — suma apare în rândurile normale de TVA colectată, doar decalată în timp.
- **Se introduce în decont TVA-ul aferent facturilor emise neîncasate**, deși acesta rămâne în 4428 până la momentul încasării.
- **Se omite bifarea „furnizorul aplică TVA la încasare" pe facturile de achiziție**, ceea ce lasă nedeclarată amânarea dreptului de deducere de la rândul B1.

## Ce face iConta.eu

Flagul `tva_la_incasare` din profilul firmei declanșează, pentru sumele din decontări (încasări/plăți alocate pe facturi), trecerea prin `tva_incasare.tva_din_incasare()` per cotă, cu excepție explicită pentru taxarea inversă. Bifa „furnizorul aplică TVA la încasare", de pe factura de achiziție, e **manuală** — aplicația nu verifică live Registrul public al persoanelor care aplică sistemul, administrat de ANAF conform art. 324 alin. (16); bifa rămâne pe răspunderea contabilului.

[iConta.eu](/)
