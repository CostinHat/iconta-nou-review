---
title: "Donația de produse din stoc: tratament contabil"
description: "De ce donarea unor bunuri din stoc, pentru care TVA a fost dedusă la achiziție, e asimilată unei livrări cu plată și trebuie taxată la ieșirea din gestiune."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Donația de produse din stoc: tratament contabil

Când o firmă donează bunuri din propriul stoc — mărfuri, produse finite — TVA nu dispare doar pentru că nu există o încasare. Dacă la achiziția sau producția acelor bunuri s-a dedus TVA, legea tratează donația ca pe o livrare impozabilă, cu obligația de a colecta TVA la valoarea bunurilor donate.

## Temeiul legal

::: ghid-temei
„(4) Sunt asimilate livrărilor de bunuri efectuate cu plată următoarele operațiuni: a) preluarea de către o persoană impozabilă a bunurilor mobile achiziționate sau produse de către aceasta pentru a fi utilizate în scopuri care nu au legătură cu activitatea economică desfășurată, dacă taxa aferentă bunurilor respective sau părților lor componente a fost dedusă total sau parțial; b) preluarea de către o persoană impozabilă a bunurilor mobile achiziționate sau produse de către aceasta pentru a fi puse la dispoziția altor persoane în mod gratuit, dacă taxa aferentă bunurilor respective sau părților lor componente a fost dedusă total sau parțial."
— Legea nr. 227/2015 (Codul fiscal), art. 270 alin. (4) lit. a), b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta în practică:

- Donarea unor bunuri de natura stocurilor (mărfuri, produse finite) pentru care s-a dedus TVA la intrare este **asimilată unei livrări cu plată** — firma trebuie să colecteze TVA la valoarea de piață a bunurilor donate, chiar dacă nu încasează nimic.
- Obligația nu apare dacă TVA nu a fost dedus la achiziție/producție (de exemplu bunuri cumpărate de la neplătitori de TVA sau achiziționate anterior înregistrării în scopuri de TVA) — condiția din text este explicit legată de deducerea taxei.
- Excepțiile din Codul fiscal (bunuri de mică valoare acordate gratuit în scop de reclamă, mostre, bunurile acordate gratuit din rezerva de stat ca ajutoare umanitare) nu se aplică automat unei donații obișnuite de marfă din stoc către un terț — trebuie verificate condițiile specifice ale fiecărei excepții înainte de a considera operațiunea scutită de colectarea TVA.
- Din punct de vedere contabil, donația presupune scoaterea bunurilor din gestiune (descărcare de gestiune la cost) și, separat, colectarea TVA aferentă valorii de piață a bunurilor, printr-o autofactură.

## Ce se greșește în practică

- Se scot bunurile din stoc pe cheltuială (contul de cheltuieli cu donațiile), fără să se colecteze deloc TVA, pe motiv că „nu s-a încasat nimic".
- Se presupune că orice donație e automat scutită de TVA, fără să se verifice dacă bunurile respective se încadrează la vreo excepție expresă din Codul fiscal.
- Nu se emite autofactura care justifică TVA colectată pentru bunurile acordate gratuit, deși aceasta e documentul cerut pentru livrările/prestările către sine.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un flux dedicat pentru donația de produse din stoc**. Aplicația are module pentru descărcarea de gestiune la vânzare (`core/stocuri.py`, cu funcția `descarcare_gv`), pentru sponsorizări deductibile prin credit fiscal (`core/sponsorizari.py`, cu funcțiile `credit_sponsorizare` și `nota_sponsorizare`, aplicabile însă sponsorizărilor în bani sau prin contracte de sponsorizare, nu donațiilor directe de marfă), dar niciunul dintre ele nu calculează automat TVA colectată la o livrare către sine conform art. 270 alin. (4). Înregistrarea corectă — descărcare de gestiune la cost plus autofactură cu TVA colectată — rămâne o operațiune manuală, pe baza documentației întocmite de contabil.

[iConta.eu](/)
