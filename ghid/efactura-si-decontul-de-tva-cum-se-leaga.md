---
title: e-Factura și decontul de TVA — cum se leagă?
description: Facturile emise și primite (inclusiv prin RO e-Factura) intră automat în D300 pe fereastra fiscală a firmei, dar codul separă colectata de deductibilă pe cote și marchează operațiunile speciale doar dacă factura e etichetată corect.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# e-Factura și decontul de TVA — cum se leagă?

Decontul D300 nu se completează de la zero în fiecare lună — se construiește automat din facturile deja înregistrate în aplicație, indiferent dacă au fost emise/primite prin RO e-Factura sau introduse manual. Legătura dintre factură și rândul din D300 se face după cotă, tipul operațiunii și fereastra fiscală a firmei.

## Temeiul legal

::: ghid-temei
„(1) Exigibilitatea taxei intervine la data la care are loc faptul generator.
(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: a) la data
emiterii unei facturi, înainte de data la care intervine faptul generator; [...] b) la data
la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care
intervine faptul generator.”
— art.282 alin.(1)-(2) Cod fiscal

„Sunt, de asemenea, scutite de taxă următoarele: a) livrările intracomunitare de bunuri
către o persoană impozabilă sau către o persoană juridică neimpozabilă care acționează ca
atare în alt stat membru decât cel în care începe expedierea sau transportul bunurilor, care
îi comunică furnizorului un cod valabil de înregistrare în scopuri de TVA, atribuit de
autoritățile fiscale din alt stat membru [...]”
— art.294 alin.(2) lit.a) Cod fiscal
:::

## Cum ajung facturile din decontul propriu în D300

Generarea decontului urmează un flux fix: `pull` citește toate facturile din perioada fiscală relevantă (ținând cont dacă firma depune lunar, trimestrial, semestrial sau anual), apoi `calcul_d300` separă strict TVA colectată (pe facturile de livrare) de TVA deductibilă (pe facturile de achiziție): colectata se calculează automat pe cotele 21%, 11% și 9% tranzitoriu, dar deductibila doar pe 21% și 11% — cota 9% deductibilă nu se auto-emite (validatorul instalat o respinge), ci se semnalează doar ca avertisment, pentru declarare manuală ulterioară.

Operațiunile speciale nu se declară „la grămadă” — se recunosc automat doar dacă factura are marcajul corect:

- livrare intracomunitară de bunuri, scutită conform art.294 alin.(2) — dacă factura e marcată corespunzător ca operațiune intracomunitară (`axa_ic`);
- export către un stat non-UE — dacă factura e marcată corespunzător pentru țară terță (`tert_tara`);
- taxare inversă internă (art.331) — dacă factura e marcată `taxare_inversa`, atât la furnizor cât și la beneficiar, cu obligația ca suma colectată și cea deductibilă să fie identice (nu se acceptă un decont în care doar una din cele două e completată);
- achiziție/livrare intracomunitară de servicii, reclasificată prin panoul dedicat D390 (declarația recapitulativă intracomunitară), sursă unică `core.d390`.

O cotă taxabilă care nu se încadrează în 21/11/9% (de exemplu un rest de 19% sau 5% dintr-o cotă veche) nu are un rând valid în formularul curent — nu e ignorată tacit, ci semnalată ca avertisment de sub-declarare, pentru ca cineva să decidă manual unde se încadrează.

## Ce se greșește în practică

- Facturi lăsate în stare de ciornă/nefinalizate — nu intră automat în decont, deși contabilul le consideră deja „emise”.
- Facturi de export sau intracomunitare introduse fără marcajul corespunzător — ajung tratate ca livrări interne taxabile, cu TVA colectată greșit.
- Taxare inversă marcată doar pe una dintre facturi (fie doar la furnizor, fie doar la beneficiar) — decontul se blochează la generare pentru că suma colectată nu oglindește suma deductibilă.
- Confuzie între data emiterii facturii și data faptului generator — mai ales la avansuri, unde exigibilitatea e la data încasării, nu la data facturii.
- Presupunerea că orice cotă introdusă pe factură (ex. 19%, 5% vechi) se regăsește automat undeva în decont — de fapt genereză doar un avertisment, fără rând alocat automat.

## Ce face iConta.eu

`pull(conn, schema, perioada)` citește facturile firmei direct din baza de date, pe fereastra fiscală calculată din tipul de decont (lunar/trimestrial/semestrial/anual). `calcul_d300` face calculul pur: separă colectata (pe cote 21/11/9%) de deductibilă (pe cote 21/11% — cota 9% deductibilă nu se auto-emite) și identifică automat livrările intracomunitare, exportul și taxarea inversă din marcajele facturii (`tert_tara`, `taxare_inversa`, `axa_ic`), fără să le amestece tacit cu rândurile introduse manual de contabil — orice suprapunere între un rând derivat automat și unul introdus manual oprește generarea cu eroare explicită, ca să nu se numere de două ori aceeași operațiune.

[iConta.eu](/)
