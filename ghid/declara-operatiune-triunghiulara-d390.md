---
title: "Cum se declară o operațiune triunghiulară în D390?"
description: "De ce codul T al unei operațiuni triunghiulare nu se derivă niciodată automat din facturi și trebuie introdus manual în panoul de clasificare D390."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară o operațiune triunghiulară în D390?

O operațiune triunghiulară (firma din România cumpără dintr-un stat membru și revinde către un al treilea, fără ca bunurile să tranziteze România) are propriul cod în declarația recapitulativă — **T** — distinct de codul obișnuit de livrare intracomunitară de bunuri (L). Spre deosebire de o livrare sau achiziție intracomunitară „simplă", care se derivă automat din facturi, operațiunea triunghiulară nu se recunoaște niciodată singură — trebuie clasificată manual.

## Temeiul legal

::: ghid-temei
„Se completează cu tranzacţiile intracomunitare efectuate, în următoarea ordine: a) livrări intracomunitare de bunuri (L); b) livrări ulterioare de bunuri efectuate în cadrul unei operaţiuni triunghiulare (T); [...]"
— OPANAF 705/2020, Anexa 2, Instrucțiuni pct. 1 (sursă: anaf_surse/opanaf_705_2020_d390.txt)
:::

- Coloana „Cod operator intracomunitar" pentru tipul T cere „codul de identificare în scopuri de TVA al persoanei beneficiare a livrării ulterioare, din al treilea stat membru, pe baza căruia cumpărătorul revânzător din România i-a efectuat livrarea ulterioară" — deci codul de TVA al **cumpărătorului final**, nu al furnizorului inițial.
- Codul partenerului e **obligatoriu** pentru operațiunile de tip T (alături de L, P, R) — spre deosebire de achizițiile de bunuri (A) sau de servicii (S), unde codul poate lipsi în anumite situații.
- Tipul „Tipul operațiunii" trece explicit T „pentru livrări în cadrul unei operațiuni triunghiulare" — un cod distinct de L, care nu trebuie confundat cu o livrare intracomunitară obișnuită doar pentru că partenerii sunt din UE.

## Ce se greșește în practică

- Se declară operațiunea triunghiulară sub codul L (livrare intracomunitară obișnuită), pentru că factura arată similar cu o livrare IC normală — distincția L/T depinde de traseul fizic al mărfii (dacă bunurile au tranzitat sau nu România), nu doar de partenerii implicați.
- Se așteaptă ca aplicația să recunoască singură operațiunea triunghiulară din datele facturii — mecanismul de auto-derivare din facturi produce implicit codul L pentru orice livrare de bunuri către UE; codul T nu e niciodată dedus automat.
- Se omite codul de TVA al partenerului la introducerea manuală a operațiunii T — codul e obligatoriu pentru acest tip, spre deosebire de tipurile A/S, unde poate lipsi în condiții specifice.

## Ce face iConta.eu

Motorul D390 al iConta.eu **nu derivă niciodată automat** o operațiune de tip T din facturi — orice livrare emisă e implicit clasificată ca L (bunuri). Pentru a declara o operațiune triunghiulară, contabilul trebuie fie să **reclasifice** manual o operațiune auto-derivată din L în T (din panoul de clasificare, pasul 2 al declarației), fie să adauge o **linie pur manuală** de tip T, dacă operațiunea nu are corespondent într-o factură emisă prin aplicație. Codul partenerului e cerut obligatoriu la introducere, conform aceleiași reguli din instrucțiunile ANAF.

O limitare importantă: dacă factura a fost emisă prin ecranul dedicat de „Livrare/prestare intracomunitară" al aplicației, câmpul care marchează tipul „bunuri/servicii" se înghețează la crearea documentului și decide definitiv tipul din D390 — reclasificarea manuală în T nu mai are efect asupra unei astfel de facturi, deși panoul continuă să afișeze un selector funcțional. Pentru facturi emise prin ecranul obișnuit de emitere (fără acest câmp completat), reclasificarea manuală spre T funcționează fără restricții.

[iConta.eu](/)
