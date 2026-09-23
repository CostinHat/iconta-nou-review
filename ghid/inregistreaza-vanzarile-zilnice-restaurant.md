---
title: Cum se înregistrează vânzările zilnice ale unui restaurant?
description: La un restaurant care vinde prin bonuri fiscale, vânzarea zilnică nu se înregistrează bon cu bon, ci centralizat, prin Raportul Z al casei de marcat — pe cote de TVA și pe tip de încasare.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se înregistrează vânzările zilnice ale unui restaurant?

Un restaurant care vinde populației (fără să emită factură la fiecare masă) nu are, contabil, o linie per bon fiscal — are o singură notă contabilă pe zi, centralizată din Raportul Z al casei de marcat.

## Temeiul legal

::: ghid-temei
„(10) Prin excepție de la prevederile alin. (6) lit. a), persoana impozabilă este scutită de obligația emiterii facturii pentru următoarele operațiuni, cu excepția cazului în care beneficiarul solicită factura: a) livrările de bunuri prin magazinele de comerț cu amănuntul și prestările de servicii către populație, pentru care este obligatorie emiterea de bonuri fiscale [...] conform Ordonanței de urgență a Guvernului nr. 28/1999 privind obligația operatorilor economici de a utiliza aparate de marcat electronice fiscale, republicată, cu modificările și completările ulterioare" — Codul fiscal, art. 319 alin. (10) lit. a)
:::

## Mecanismul

Casa de marcat fiscală emite bon la fiecare vânzare — dar acesta nu se emite ca factură (art. 319 alin. (10) lit. a) scutește exact acest tip de vânzare de obligația facturării, cu excepția cazului în care clientul cere explicit factură). Ce se înregistrează contabil e **totalul zilei**, extras din Raportul Z pe care casa de marcat îl produce la închiderea zilei fiscale — separat pe cote de TVA (11% pentru mâncare, 21% pentru alcool și băuturi excluse de la cota redusă) și pe tip de plată (numerar, card).

Nota contabilă rezultată: `5311 = 707` pentru partea din numerar, `5125 = 707` pentru card, `707 = 4427` pentru TVA colectată pe fiecare cotă. O singură notă pe zi (sau pe raport Z, dacă sunt mai multe case de marcat), nu una per bon.

## Ce se greșește în practică

Încercarea de a înregistra fiecare bon fiscal individual, ca și cum ar fi o factură — inutil de laborios și fără sens contabil, atâta vreme cât Raportul Z centralizează deja corect totalurile pe cote și pe tip de plată. A doua greșeală: ignorarea excepției de la cota de 11% pentru băuturile alcoolice și pentru cele nealcoolice cu cod NC 2202 (energizante, sucuri, ape gazoase/aromatizate cu zahăr) — acestea rămân la 21%, chiar dacă apar pe același bon cu mâncarea de la 11%.

## Ce face iConta.eu

Ecranul „Raport Z" preia totalurile fie prin import direct al fișierului AMEF (care citește orice cotă TVA apărută efectiv în raport, nu doar 11%/21%), fie prin introducere manuală pe cele două cote fixe, cu numerar și card. Aplicația generează automat nota contabilă corespunzătoare — nu e nevoie de o notă separată pentru fiecare bon fiscal emis în cursul zilei.

[iConta.eu](/)
