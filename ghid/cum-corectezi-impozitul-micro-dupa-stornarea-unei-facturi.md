---
title: Cum corectezi impozitul micro după stornarea unei facturi?
description: Dacă factura stornată aparține exercițiului financiar curent, minusul intră firesc în veniturile trimestrului; dacă aparține unui an anterior deja închis, corecția fiscală trebuie tratată manual — motorul de storno nu distinge cele două situații.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum corectezi impozitul micro după stornarea unei facturi?

Impozitul pe veniturile microîntreprinderilor se calculează trimestrial, pe baza veniturilor perioadei. O stornare afectează direct această bază — dar felul corect de a o trata depinde de un singur factor pe care sistemul, azi, nu îl verifică automat: din ce exercițiu financiar face parte factura originală.

## Temeiul legal

::: ghid-temei
„65. ‐ (1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. (2) Corectarea erorilor se efectuează la data constatării lor."

„67. ‐ (1) Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. (2) Corectarea erorilor semnificative aferente exercițiilor financiare precedente se efectuează pe seama rezultatului reportat (contul 1174 «Rezultatul reportat provenit din corectarea erorilor contabile»). (3) Erorile nesemnificative aferente exercițiilor financiare precedente se corectează, de asemenea, pe seama rezultatului reportat. Totuși, potrivit politicilor contabile aprobate, erorile nesemnificative pot fi corectate pe seama contului de profit și pierdere." — OMFP 1802/2014, secțiunea 2.5.2, pct. 65-68

„69. ‐ Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roşu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă şi programele informatice utilizate." — OMFP 1802/2014, pct. 69
:::

## De ce contează anul facturii originale

Regula de la pct. 69 (stornare cu minus pe contul de venit) se aplică **strict operațiunilor din exercițiul financiar curent**. Dacă factura originală e din anul curent, un storno care reduce 707/701/703/704 cu semnul minus reduce corect și baza impozabilă a trimestrului curent pentru impozitul micro.

Dacă însă factura originală e dintr-un an financiar anterior, deja închis (situații financiare depuse), regula corectă e alta: pct. 67 alin. (2) cere trecerea corecției prin contul 1174, nu prin diminuarea directă a veniturilor curente. O reducere de venit înregistrată azi, prin minus pe 707, pentru o factură emisă și taxată în urmă cu un an, ar micșora artificial baza de impozitare micro a trimestrului curent — deși venitul respectiv a fost deja raportat și impozitat în perioada corectă, în anul anterior.

::: ghid-exemplu
O factură de 5.000 lei emisă în decembrie anul trecut se stornează azi. Dacă motorul postează automat -5.000 lei pe 707 în trimestrul curent, baza impozabilă a acestui trimestru scade cu 5.000 lei — deși venitul aparținea fiscal anului trecut. Corect ar fi ca reducerea să treacă prin 1174, iar corecția impozitului micro al anului trecut să se facă printr-o declarație rectificativă pentru acea perioadă, nu prin diminuarea trimestrului curent.
:::

## Ce se greșește în practică

- Se lasă storno-ul să reducă automat veniturile trimestrului curent, indiferent de anul facturii originale.
- Nu se verifică dacă factura stornată aparține unui exercițiu financiar deja închis, cu situații financiare depuse.
- Nu se depune declarație rectificativă pentru perioada fiscală în care venitul original a fost efectiv raportat.
- Se tratează orice storno ca „eroare nesemnificativă", fără o evaluare reală a pragului de semnificație stabilit prin politica contabilă proprie.
- Se confundă corecția contabilă (cont 1174 vs. cont de venit curent) cu simpla generare a facturii de storno, care e doar un document fiscal, nu o decizie de încadrare contabilă.

## Ce face iConta.eu

Funcția de storno construiește întotdeauna documentul nou cu data curentă (`datetime.date.today()`), indiferent de anul facturii originale, iar nota automată generată din liniile cu cantitate negativă scrie mereu pe conturile de venit curent (707/701/703/704) cu semn minus — niciodată pe 1174. Sistemul nu verifică și nu semnalează dacă factura originală aparține unui exercițiu financiar anterior celui curent. Pentru facturi stornate din ani anteriori, corecția prin 1174 și eventuala rectificare a declarației de impozit micro pentru perioada corectă rămân în sarcina contabilului — sunt pași manuali, nu automatizați de motorul de contare.

[iConta.eu](/)
