---
title: "Cum se înregistrează numerarul încasat prin casa de marcat?"
description: "Nota contabilă corectă pentru numerarul încasat prin aparatul de marcat electronic fiscal, direct pe venituri, conform planului de conturi din OMFP 1802/2014."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se înregistrează numerarul încasat prin casa de marcat?

Vânzarea cu amănuntul, plătită direct cu numerar la casa de marcat, nu trece de regulă prin contul de clienți — se înregistrează direct pe conturile de venituri, la data raportului fiscal de închidere zilnică.

## Temeiul legal

::: ghid-temei
„Contul 531 «Casa» [...] este un cont de activ. În debitul contului 531 «Casa» se înregistrează: [...] – sumele încasate din servicii prestate, vânzarea mărfurilor și alte activități (704, 707, 708, 4427)."
— OMFP 1802/2014, funcțiunea contului 531 „Casa" (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Nota contabilă tipică pentru încasările zilei, preluate din raportul fiscal de închidere zilnică:

- **531 „Casa" = 707 „Venituri din vânzarea mărfurilor" + 4427 „TVA colectată"**, pentru vânzarea de mărfuri cu amănuntul, plătită integral în numerar.
- **531 „Casa" = 704 „Venituri din lucrări executate și servicii prestate" + 4427**, pentru servicii prestate cu plată în numerar.
- Planul de conturi confirmă explicit corespondența directă cu conturile de venituri (704, 707, 708) și cu TVA colectată (4427) — nu e nevoie, la vânzarea cu amănuntul prin AMEF, de trecerea prin 4111 „Clienți", pentru că nu există o creanță intermediară: încasarea e simultană cu vânzarea.
- Suma care intră pe 531 e cea din **raportul fiscal de închidere zilnică**, nu suma fiecărui bon în parte — un singur set de note contabile pe zi, nu pe tranzacție.

## Ce se greșește în practică

- Se înregistrează vânzarea prin 4111 „Clienți", urmată de o încasare separată — inutil de dublă pentru o vânzare cu plată imediată, integral în numerar, și incoerent cu funcțiunea contului 531 din normă.
- Se omite defalcarea pe conturi de venituri diferite (707 mărfuri vs. 704 servicii) când activitatea combină ambele — TVA colectată corespunde fiecărui tip de venit, iar defalcarea greșită denaturează raportarea.
- Se înregistrează suma brută a raportului Z direct ca venit, fără separarea TVA colectate (4427) — venitul contabil trebuie înregistrat fără TVA, nu la valoarea totală încasată.

## Ce face iConta.eu

La data acestui ghid, `core/casa.py` conține `regula_cont_casa()`, care generează nota contabilă pentru operațiunile de casă introduse manual — dar doar pentru scopurile pe care le recunoaște azi: încasare de la client (5311 = 4111), plată către furnizor (401 = 5311), ridicare și depunere la bancă; pentru orice altă situație, funcția ridică explicit o eroare (`scop/tip nesuportat`). Vânzarea cu amănuntul prin AMEF are însă un flux dedicat, separat: `core/amef_import.py` (`parseaza_raport_z()`) preia raportul fiscal de închidere zilnică, iar `core/uc_tenants.py` (`horeca_import_amef()`) generează automat nota-ciornă exact pe structura descrisă mai sus — **5311 = 707 pentru numerar** (respectiv **5125 = 707** pentru încasările prin card/altele), cu linie separată **707 = 4427** pentru TVA colectată pe fiecare cotă din raportul Z. Preluarea sumei din raportul Z, cu separarea pe conturi de venituri și TVA colectată, e deci automată; rămâne manuală doar verificarea notei-ciornă rezultate față de Z-ul tipărit.

[iConta.eu](/)
