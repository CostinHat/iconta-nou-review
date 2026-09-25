---
title: "Cum împac casa de marcat cu vânzările la HoReCa"
description: "Obligația de casă de marcat pentru încasările cu numerar/card la un restaurant sau local, conectarea la ANAF și reconcilierea raportului Z cu evidența contabilă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum împac casa de marcat cu vânzările la HoReCa

Într-un restaurant sau local HoReCa, aproape toate vânzările sunt încasări directe de la clienți — numerar sau card — ceea ce declanșează obligația de casă de marcat pentru fiecare tranzacție. Problema practică pentru contabilitate nu e dacă se folosește casa de marcat, ci cum se reconciliază sumele din raportul Z zilnic cu notele contabile de venituri, TVA și modalități de încasare.

## Temeiul legal

::: ghid-temei
„Operatorii economici care încasează, integral sau parțial, cu numerar sau prin utilizarea cardurilor de credit/debit sau a substitutelor de numerar contravaloarea bunurilor livrate cu amănuntul, precum și a prestărilor de servicii efectuate direct către populație sunt obligați să utilizeze aparate de marcat electronice fiscale."
— OUG 28/1999, art. 1 alin. (1) (sursă: anaf_surse/oug_28_1999.html)
:::

Ce presupune, concret, reconcilierea HoReCa:

- Fiecare casă de marcat trebuie conectată la distanță la sistemul ANAF, pentru transmiterea de date fiscale în timp real — o obligație suplimentară față de simpla emitere de bonuri fiscale: „operatorii economici [...] au obligația de a asigura conectarea la distanță a aparatelor de marcat electronice fiscale, în vederea transmiterii de date fiscale către Agenția Națională de Administrare Fiscală" (OUG 28/1999, art. 3^1 alin. (4)).
- Raportul Z de la finalul zilei conține totalurile pe cotă de TVA (structura standard din OPANAF 146/2018, secțiunea II.7) și defalcarea pe modalitate de plată (numerar, card, tichete de masă, vouchere) — aceste totaluri trebuie să corespundă cu notele contabile de încasare din ziua respectivă.
- Diferențele frecvente la HoReCa apar din bacșișul introdus prin card (care nu e venit al firmei, dar trece prin același terminal de plată) și din anulările/stornările de comenzi, care trebuie reflectate corect atât în casa de marcat, cât și în contabilitate, nu doar „netuite" din total.
- Vânzările prin platforme de livrare (aplicații de food delivery) ridică o întrebare separată: dacă plata se face direct în aplicație, fără numerar/card la local, emiterea bonului fiscal urmează regulile specifice stabilite de ANAF pentru aceste circuite, nu regula generală de emitere la fiecare încasare directă.

## Ce se greșește în practică

- Se înregistrează în contabilitate direct totalul din raportul Z, fără să se separă bacșișul încasat prin card de venitul efectiv al firmei — bacșișul distribuit angajaților are un regim contabil și fiscal distinct.
- Se ignoră discrepanțele mici, recurente, dintre soldul de casă fizic și totalul din raportul Z, presupunând că „se echilibrează singure" — aceste diferențe sunt exact ce verifică un control fiscal la o firmă HoReCa.
- Se presupune că o casă de marcat neconectată la sistemul ANAF (din motive tehnice, neremediate) e doar o problemă tehnică temporară — legea o tratează ca pe o încălcare a obligației de conectare, sancționabilă distinct de emiterea bonurilor fiscale.

## Ce face iConta.eu

iConta.eu importă rapoartele Z direct din fișierul exportat de casa de marcat (XML simplu sau fișier semnat p7b conform OPANAF 146/2018), extrăgând automat totalurile pe cotă de TVA, numărul de bonuri și defalcarea pe modalitate de plată (numerar, card, tichete de masă, vouchere etc.), pe care le transformă în notă contabilă. Aplicația nu se conectează însă direct la casa de marcat pentru citire în timp real și nu gestionează ea însăși conectarea aparatului la sistemul ANAF — acestea rămân configurări la nivelul casei de marcat, din afara iConta.eu; separarea bacșișului de venitul propriu-zis al firmei, dacă nu reiese distinct din structura raportului Z, rămâne o verificare a contabilului.

[iConta.eu](/)
