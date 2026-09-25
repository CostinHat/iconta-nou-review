---
title: "Care este monografia contabilă pentru recepția mărfurilor?"
description: "Funcțiunea contului 371 «Mărfuri» la recepția unei achiziții de la furnizor, potrivit reglementărilor contabile OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Care este monografia contabilă pentru recepția mărfurilor?

Recepția unei achiziții de mărfuri de la furnizor se înregistrează în debitul contului 371 „Mărfuri", la valoarea de preț de înregistrare stabilită de firmă (cost de achiziție sau preț cu amănuntul, după politica contabilă adoptată), în contrapartidă cu datoria față de furnizor.

## Temeiul legal

::: ghid-temei
„GRUPA 37 «MĂRFURI» [...] Contul 371 «Mărfuri» Cu ajutorul acestui cont se ține evidența existenței și mișcării stocurilor de mărfuri. Contul 371 «Mărfuri» este un cont de activ. În debitul contului 371 «Mărfuri» se înregistrează: – valoarea la preț de înregistrare a mărfurilor achiziționate (401, 408, 446, 327, 542); [...] – valoarea la preț de înregistrare a mărfurilor achiziționate de la entități afiliate sau de la entități asociate și entități controlate în comun (451, 453); [...] – valoarea mărfurilor aduse de la terți (357, 401); [...] – valoarea adaosului comercial și taxa pe valoarea adăugată neexigibilă, în situația în care evidența mărfurilor se ține la preț cu amănuntul (378, 4428)."
— OMFP 1802/2014, Cap. 16 „Funcțiunea conturilor", Grupa 37, Contul 371 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Nota contabilă tipică, la recepția unei achiziții de mărfuri de la un furnizor intern, plătitor de TVA:

- **La cost de achiziție** (evidență cantitativ-valorică): 371 „Mărfuri" = 401 „Furnizori", cu TVA aferentă în debitul contului 4426 „TVA deductibilă".
- **La preț cu amănuntul** (evidență global-valorică, uzuală în retail): 371 „Mărfuri" = 401 „Furnizori" + 378 „Diferențe de preț la mărfuri" (adaosul comercial) + 4428 „TVA neexigibilă" — mecanismul specific comerțului cu amănuntul, unde TVA devine exigibilă abia la vânzare.
- Dacă achiziția vine de la o entitate afiliată sau asociată, conturile de furnizor sunt 451/453 în loc de 401 — restul mecanismului rămâne identic.
- Cheltuielile conexe recepției (transport, manipulare), dacă nu sunt incluse direct în prețul de achiziție facturat de furnizor, se adaugă la costul de intrare, conform definiției costului de achiziție din reglementări (OMFP 1802/2014, pct. 8 subpct. 6).

## Ce se greșește în practică

- Se înregistrează recepția direct pe cheltuieli (607 „Cheltuieli privind mărfurile"), în loc de intrare în stoc pe 371 — eroare care denaturează atât rezultatul lunii recepției, cât și pe cel al lunii vânzării.
- Se amestecă metoda de evidență la cost de achiziție cu cea la preț cu amănuntul în aceeași gestiune, fără o politică contabilă clară — adaosul comercial (378) și TVA neexigibilă (4428) au sens doar în evidența global-valorică.
- Se omite includerea cheltuielilor de transport facturate separat în costul de intrare al mărfii, tratându-le direct ca o cheltuială de exploatare a lunii, chiar dacă sunt direct atribuibile achiziției.

## Ce face iConta.eu

La data acestui ghid, iConta.eu oferă, prin modulul `core/stocuri.py`, funcția `nir_gv`, care generează nota de recepție pentru gestiunea global-valorică (cu adaos comercial și TVA neexigibilă, conturile 371/378/4428), inclusiv calculul coeficientului de repartizare (K) folosit ulterior la descărcarea gestiunii. Pentru evidența la cost de achiziție simplu, aplicația oferă evidența contabilă generală (jurnal, fișă de cont), pe care contabilul o folosește pentru notele de recepție care nu trec prin gestiunea global-valorică.

[iConta.eu](/)
