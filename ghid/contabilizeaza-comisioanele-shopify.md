---
title: "Cum se contabilizează comisioanele Shopify?"
description: "Cum se înregistrează în contabilitate comisioanele reținute de o platformă precum Shopify și ce presupune TVA pentru un serviciu facturat din afara României."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se contabilizează comisioanele Shopify?

Comisioanele reținute de o platformă de comerț online (procesare plăți, abonament, tranzacții) sunt o cheltuială cu servicii prestate de terți, dar au o particularitate: furnizorul e de regulă o firmă din afara României, ceea ce schimbă modul de tratare a TVA față de un furnizor local.

## Temeiul legal

::: ghid-temei
„Contul 622 «Cheltuieli privind comisioanele și onorariile» Cu ajutorul acestui cont se ține evidența cheltuielilor reprezentând comisioanele datorate pentru cumpărarea sau vânzarea titlurilor de valoare imobilizate sau a celor de plasament, comisioanele de intermediere, onorariile de consiliere, contencios, expertizare, precum și a altor cheltuieli similare."
— OMFP 1802/2014, funcțiunea conturilor, grupa 62 „Cheltuieli cu alte servicii executate de terți" (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce presupune, concret, înregistrarea corectă:

- Comisionul se înregistrează ca o cheltuială de exploatare (cont 622 „Cheltuieli privind comisioanele și onorariile" sau, după caz, 628 „Alte cheltuieli cu serviciile executate de terți"), nu ca o diminuare directă a veniturilor din vânzări.
- Dacă furnizorul (platforma) este stabilit în alt stat membru UE sau în afara UE, iar serviciul are locul prestării în România, factura primită intră, de regulă, sub incidența taxării inverse (reverse-charge) — TVA se autolichidează, nu se plătește furnizorului.
- Documentul justificativ (extras de cont Shopify, factura/invoice emisă de platformă) trebuie păstrat și corelat cu suma reținută efectiv din încasările clienților, pentru ca cifra de afaceri raportată să fie cea brută, nu cea netă de comision.

## Ce se greșește în practică

- Se înregistrează în contabilitate doar suma netă încasată (după scăderea comisionului), fără să se evidențieze separat venitul brut din vânzare și cheltuiala cu comisionul — asta denaturează cifra de afaceri raportată.
- Se ignoră taxarea inversă pe factura de comision de la un furnizor extern, tratând-o ca pe o factură internă fără TVA.
- Se confundă comisionul de platformă (622/628) cu un comision bancar (627) — clasificarea contabilă diferă, deși efectul asupra rezultatului e similar.

## Ce face iConta.eu

iConta.eu nu are o integrare dedicată cu Shopify sau cu alte platforme de comerț online — nu importă automat extrasele de tranzacții sau comisioanele reținute. Aplicația oferă însă evidența contabilă generală pentru astfel de facturi: modulul de contare a facturilor (`core/contare_facturi.py`) generează notele contabile pentru facturile de achiziție introduse manual, iar modulul de operațiuni intracomunitare (`core/intracomunitar.py`) tratează corect TVA pentru serviciile primite de la furnizori din afara României — cu taxare inversă 4426=4427 pentru firmele plătitoare de TVA cu drept de deducere, respectiv TVA nedeductibilă (intrată în costul achiziției) pentru firmele înregistrate doar conform art. 317. (Modulul `core/taxare_inversa.py` e altceva: taxare inversă internă, art. 331 Cod fiscal, pentru categorii specifice de bunuri — deșeuri, cereale, energie electrică, telefoane/console sub prag etc. — nu pentru servicii de la furnizori din afara României.) Introducerea facturii/extrasului de comision de la Shopify rămâne, la acest moment, un pas manual al contabilului.

[iConta.eu](/)
