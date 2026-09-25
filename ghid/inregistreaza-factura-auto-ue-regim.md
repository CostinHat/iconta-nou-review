---
title: "Cum se înregistrează o factură auto UE cu regim de marjă?"
description: "Ce înseamnă pentru cumpărătorul român o factură de la un dealer auto din UE care aplică regimul special de marjă, și de ce nu e o achiziție intracomunitară obișnuită."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează o factură auto UE cu regim de marjă?

Când cumperi un autoturism second-hand de la un dealer dintr-un alt stat membru UE care aplică, pentru acea vânzare, regimul special de marjă (echivalentul art. 312 din Codul fiscal, aplicat de vânzător în statul lui), factura arată altfel decât la o achiziție intracomunitară obișnuită: TVA e inclus în preț, calculat de vânzător doar pe marja lui de profit, nu pe valoarea integrală a mașinii, și factura nu conține un cod de TVA „intracomunitar" evidențiat separat. Consecința pentru cumpărătorul din România nu e doar o chestiune de formă a facturii — e o achiziție care iese complet din sfera taxării intracomunitare.

## Temeiul legal

::: ghid-temei
„(8) Nu sunt considerate operațiuni impozabile în România: [...] c) achizițiile intracomunitare de bunuri second-hand, opere de artă, obiecte de colecție și de antichități, în sensul prevederilor art. 312, atunci când vânzătorul este o persoană impozabilă revânzătoare, care acționează în această calitate, iar bunurile au fost taxate în statul membru de unde sunt furnizate, conform regimului special pentru intermediarii persoane impozabile, în sensul art. 313 și 326 din Directiva 112, sau vânzătorul este organizator de vânzări prin licitație publică, care acționează în această calitate, iar bunurile au fost taxate în statul membru furnizor, conform regimului special, în sensul art. 333 din Directiva 112;"
— Codul fiscal (Legea 227/2015), art. 268 alin. (8) lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Practic, legea spune că o astfel de achiziție **nu e deloc o operațiune impozabilă în România**, cu condiția cumulativă a trei elemente:

- vânzătorul din UE e o **persoană impozabilă revânzătoare** (dealer auto second-hand, în sensul art. 312) care acționează ca atare, nu ca simplu particular;
- mașina a fost efectiv **taxată în regim special în statul membru de origine** — adică vânzătorul a aplicat marja lui de profit, nu regimul normal de TVA;
- achiziția privește exact categoria de bunuri de la art. 312 (bunuri second-hand, aici — un autoturism uzat).

Când toate trei sunt îndeplinite, cumpărătorul din România **nu datorează TVA prin taxare inversă** pe această achiziție, spre deosebire de o achiziție intracomunitară obișnuită de bunuri.

## Ce se greșește în practică

- Se tratează orice factură auto din UE ca achiziție intracomunitară „normală" și se aplică automat taxarea inversă (autolichidarea TVA), fără să se verifice dacă vânzătorul a facturat în regim de marjă.
- Se caută pe factură un cod de TVA intracomunitar „vizibil" al operațiunii și, negăsindu-l, se presupune greșit că lipsește ceva de la vânzător, în loc să se recunoască tiparul specific facturii în regim de marjă (TVA inclus în preț, fără linie de TVA separată pe valoarea totală).
- Se cere vânzătorului din UE o factură „obișnuită", deși el e obligat, dacă aplică regimul de marjă, să menționeze acest lucru pe factură — nu are de unde să emită alt tip de document pentru aceeași tranzacție.

## Ce face iConta.eu

Această situație privește **achiziția** unui autoturism în regim de marjă, dinspre cumpărător. iConta.eu nu are, la data acestui ghid, un circuit dedicat de înregistrare a unei achiziții (intracomunitare sau nu) de bunuri second-hand în regim de marjă — verificat: modulul de calcul al regimului de marjă (`core/tva_marja.py`) nu conține nicio funcție de achiziție, doar de **vânzare** (folosită de operațiunile „Vânzare regim marjă (second-hand)" și „Marjă agenții de turism" din ecranul Operațiuni).

Ce există în aplicație pe partea de regim de marjă e strict dinspre vânzare: motorul de calcul al marjei (funcționalitatea „Regim special marjă") și, separat, un raport de citire („Jurnal regim marjă") care afișează lunar notele deja înregistrate cu acest tip de vânzare. Niciuna din ele nu acoperă înregistrarea unei achiziții ca aceasta. Contabilul trebuie, azi, să introducă manual nota contabilă a achiziției (mașina intră în gestiune/imobilizări la costul de achiziție, fără linie de TVA deductibil, exact fiindcă art. 268 alin. (8) scoate operațiunea din sfera taxării).

[iConta.eu](/)
