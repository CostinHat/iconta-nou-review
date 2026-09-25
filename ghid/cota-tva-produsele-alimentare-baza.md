---
title: "Cota de TVA la produsele alimentare de bază 2026"
description: "Regula legală pentru cota de TVA la alimente în 2026, cu excepțiile care readuc anumite produse la cota standard, și felul în care iConta.eu propune automat cota pe fiecare produs nou."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cota de TVA la produsele alimentare de bază 2026

Alimentele beneficiază, ca regulă, de cotă redusă de TVA. Dar legea nu tratează „alimentele" ca pe un bloc omogen: câteva categorii — băuturile alcoolice, unele băuturi nealcoolice, alimentele cu zahăr adăugat peste un anumit prag și suplimentele alimentare — sunt scoase explicit din regula redusă și rămân la cota standard. Cunoașterea acestor excepții contează la fel de mult ca regula de bază.

## Temeiul legal

::: ghid-temei
„Articolul 291 alin. (2) lit. b) livrarea următoarelor bunuri: alimente, inclusiv băuturi, destinate consumului uman și animal, animale și păsări vii din specii domestice, ale căror coduri NC se stabilesc prin normele metodologice, cu excepția: 1. băuturilor alcoolice; [...] 2. băuturilor nealcoolice care se încadrează la codul NC 2202; [...] 3. alimentelor cu zahăr adăugat, al căror conținut total de zahăr este de minimum 10 g/100 g produs, altele decât laptele praf pentru nou-născuți, sugari și copii de vârstă mică; [...] 4. suplimentelor alimentare definite de Legea nr. 56/2021 privind suplimentele alimentare, cu modificările și completările ulterioare;"
— Legea nr. 227/2015 (Codul fiscal), art. 291 alin. (2) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula de bază: alimentele și băuturile destinate consumului uman și animal intră la cota redusă, care este **11%** de la 01.08.2025 (Legea nr. 141/2025, care a abrogat cotele de 5% și 9%).
- Excepția 1 — băuturile alcoolice — rămân la cota standard, indiferent de alte caracteristici.
- Excepția 2 — băuturile nealcoolice încadrate la codul NC 2202 (băuturi răcoritoare, ape îndulcite/aromatizate etc.) — la cota standard.
- Excepția 3 — orice aliment cu zahăr adăugat ≥10 g/100 g produs — la cota standard, cu excepția specială a laptelui praf pentru nou-născuți, sugari și copii mici, care rămâne la cota redusă.
- Excepția 4 — suplimentele alimentare definite de Legea nr. 56/2021 — la cota standard, chiar dacă sunt vândute ca produse alimentare.
- Tot ce nu se încadrează la art. 291 alin. (2) rămâne la cota standard de **21%** (art. 291 alin. (1)).

## Ce se greșește în practică

- Se aplică automat 11% oricărui produs etichetat „alimentar", fără a verifica dacă se încadrează la una din cele patru excepții (alcool, băuturi NC 2202, zahăr adăugat ≥10g/100g, suplimente).
- Se tratează un suc îndulcit sau o băutură energizantă drept „aliment de bază" la cotă redusă, deși majoritatea se încadrează la excepția NC 2202 și rămân la cotă standard.
- Se ignoră pragul exact de zahăr (10 g/100 g) — un produs cu zahăr adăugat sub acest prag rămâne la cotă redusă, unul peste prag trece la cotă standard, iar diferența nu e vizibilă doar din denumire, ci necesită verificarea compoziției.
- Se presupune că vechile cote de 5% sau 9% mai există pentru alimente — de la 01.08.2025 singura cotă redusă este 11%.

## Ce face iConta.eu

În ecranul **Nomenclator produse**, la introducerea unei denumiri noi de produs alimentar, iConta.eu apelează un model AI (Claude, via API-ul Anthropic) care propune cota de TVA pe baza regulii oficiale din art. 291 — inclusiv excepțiile de mai sus, injectate explicit în instrucțiunile date modelului. Propunerea apare ca preview live (cu justificarea afișată) și poate fi întotdeauna corectată manual dintr-un selector dedicat.

Mecanismul nu este un simplu tabel de cuvinte-cheie: modelul AI evaluează denumirea în raport cu regula legală și cu excepțiile ei, iar rezultatul este validat strict — aplicația acceptă doar o cotă de 11% sau 21%; orice altă valoare sau răspuns neclar este respins și marcat ca „nedeterminat". În acest caz, iConta.eu **nu presupune automat 21%** — blochează emiterea facturii și cere cotă explicită din partea contabilului, tocmai pentru a evita ca o clasificare eronată sau ambiguă să ajungă tacit pe o factură emisă.

[iConta.eu](/)
