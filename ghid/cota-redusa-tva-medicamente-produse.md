---
title: "Cota redusă de TVA la medicamente și produse medicale"
description: "Ce cotă de TVA se aplică la medicamentele de uz uman conform art. 291 Cod fiscal și cum propune iConta.eu automat cota pe fiecare produs nou introdus în nomenclator."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cota redusă de TVA la medicamente și produse medicale

Medicamentele de uz uman beneficiază de cotă redusă de TVA, distinctă de cota standard aplicată majorității bunurilor și serviciilor. De la 1 august 2025, structura cotelor de TVA s-a simplificat: au rămas doar două cote, iar medicamentele se numără printre puținele categorii care intră la cota redusă. Atenție însă: legea vizează strict medicamentele, nu orice produs cu etichetă „medicală".

## Temeiul legal

::: ghid-temei
„Articolul 291 alin. (2) lit. a) livrarea de medicamente de uz uman"
— Legea nr. 227/2015 (Codul fiscal), art. 291 alin. (2) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Cota redusă se aplică **medicamentelor de uz uman** — textul de lege nu extinde reducerea la medicamentele de uz veterinar și nici la alte categorii conexe (dispozitive medicale, consumabile sanitare, suplimente).
- De la 01.08.2025 (Legea nr. 141/2025), a existat o reformă generală a cotelor: au fost abrogate cotele de 5% și 9%, iar cota redusă unică pentru categoriile din art. 291 alin. (2) — inclusiv medicamentele — este **11%**.
- Tot ce nu se încadrează explicit la art. 291 alin. (2) rămâne la cota standard, care este de **21%** conform art. 291 alin. (1).

## Ce se greșește în practică

- Se aplică automat cota redusă oricărui produs cu denumire de tip „farmaceutic" sau „sanitar", deși legea acoperă strict medicamentele de uz uman, nu dispozitivele medicale, consumabilele sau produsele cosmetice cu conținut farmaceutic.
- Se confundă medicamentele de uz uman cu cele de uz veterinar, care nu au același temei de reducere la lit. a).
- Se presupune că cota veche (9%, valabilă până la 01.08.2025) mai este în vigoare — de la acea dată, singura cotă redusă existentă pentru medicamente este 11%.

## Ce face iConta.eu

Din ecranul **Nomenclator produse**, când contabilul scrie o denumire de produs nou (de exemplu un medicament), iConta.eu trimite denumirea către un model AI (Claude, prin API-ul Anthropic) care propune automat cota de TVA, pe baza regulii oficiale de la art. 291 — inclusiv categoria „medicamente" cu articolul de lege citat în justificare. Propunerea apare ca preview live, cu cota și motivația afișate, și **poate fi corectată manual** printr-un selector explicit (21% / 11% / scutit conform art. 292); la corectare, sursa cotei devine „manual" în baza de date.

Important: dacă produsul (denumirea) există deja salvat în nomenclator, la o factură ulterioară cota vine direct din nomenclator, fără să se mai interogheze AI a doua oară. Dacă însă modelul AI este indisponibil sau răspunde neconcludent la o denumire complet nouă, aplicația **nu presupune tacit 21%** — marchează cota drept nedeterminată și blochează emiterea facturii până când cota este introdusă explicit. Clasificarea rămâne, în toate cazurile, o propunere verificabilă, nu o decizie automată definitivă — responsabilitatea încadrării corecte a fiecărui produs rămâne a contabilului.

[iConta.eu](/)
