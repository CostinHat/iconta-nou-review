---
title: "Cum contabilizez încasările prin POS?"
description: Încasările prin card se contabilizează pe contul 5125, distinct de numerarul din 5311, iar în iConta.eu suma respectivă vine din datele Raportului Z al casei de marcat, nu dintr-o integrare separată cu terminalul POS.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum contabilizez încasările prin POS?

Din punct de vedere contabil, o încasare prin terminal POS (card bancar) urmează planul de conturi general: banii nu trec prin casierie, ci direct printr-un cont de disponibilități în tranzit sau bancă, distinct de numerarul propriu-zis. În iConta.eu, pentru vânzările cu casă de marcat (AMEF), sursa acestei sume este Raportul Z.

## Temeiul legal

::: ghid-temei
Cotele de TVA aplicabile veniturilor din vânzare, indiferent de instrumentul de plată (numerar sau card), sunt cele din Legea nr. 227/2015 (Codul fiscal), art. 291 — de la 1 august 2025 (Legea 141/2025) există doar două cote: 21% standard și 11% cotă redusă unică; cotele de 5% și 9% au fost abrogate.
:::

Modul de plată (numerar sau card) nu schimbă cota de TVA a vânzării — schimbă doar contul de disponibilități în care intră banii.

## Cum tratează aplicația încasările prin card

Pentru firmele care folosesc ecranul „Raport Z" (import fișier AMEF sau introducere manuală a bonului Z), încasările prin card sunt tratate distinct de numerar, cu o notă contabilă de forma:

- **5311 = 707** pentru partea încasată în numerar;
- **5125 = 707** pentru partea încasată prin card **și orice alt mijloc de plată** din nomenclatorul casei de marcat (tichete de masă, bonuri valorice, voucher, credit, alte tipuri) — toate acestea sunt tratate contabil la fel ca și cardul, pe același cont 5125, nu separat pe tip;
- **707 = 4427** pentru TVA aferentă fiecărei cote reale din raport.

La importul unui fișier AMEF real, aplicația citește direct din bonul Z sumele pe fiecare tip de plată din nomenclator și le însumează pe 5125 (tot ce nu e numerar). La introducerea manuală, formularul are un singur câmp „Card", deci suma respectivă merge tot pe 5125.

## Ce se greșește în practică

- Se contabilizează greșit încasarea prin card pe 5311 (numerar), ca și cum ar fi bani lichizi în casierie — încasările prin POS nu sunt numerar și nu ar trebui să afecteze soldul de casă fizic.
- Se presupune că tichetele de masă sau voucherele au un tratament contabil separat de card — în structura notei generate din Raportul Z, toate plățile care nu sunt numerar (card, tichete, vouchere, credit) sunt grupate împreună, pe 5125.
- Se caută o integrare automată/directă cu terminalul POS pentru încasările din afara Raportului Z (de exemplu vânzări fără casă de marcat) — o asemenea integrare nu a fost identificată; mecanismul verificat funcționează exclusiv pe baza datelor din Raportul Z al casei de marcat.

## Ce face iConta.eu

Pentru firmele HoReCa/retail care folosesc ecranul „Raport Z", iConta.eu preia sumele pe tip de plată direct din datele casei de marcat (import AMEF) sau din câmpurile Numerar/Card introduse manual și generează automat notele contabile corespunzătoare: numerarul pe 5311, cardul și celelalte instrumente de plată electronice pe 5125, TVA pe 4427. Nu am identificat o integrare separată, directă cu terminale POS în afara acestui flux — dacă firma încasează prin card în alt context decât Raportul Z al casei de marcat, contabilizarea respectivă nu trece prin acest mecanism specific.

[iConta.eu](/)
