---
title: "Am uitat să corectez stocul după o stornare"
description: "De ce stornarea unei facturi de vânzare trebuie să corecteze simultan contul de clienți, veniturile, cheltuiala cu marfa și stocul, nu doar partea comercială a operațiunii."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am uitat să corectez stocul după o stornare

O factură de vânzare stornată — pentru că marfa a fost returnată sau factura a fost greșită — nu e o corecție izolată a contului de clienți. Regula contabilă cere ca stornarea să atingă simultan patru conturi, nu doar pe cele legate de partea comercială a tranzacției.

## Temeiul legal

::: ghid-temei
„330. (1) În cazul mărfurilor returnate de clienți în același exercițiu financiar în care a avut loc operațiunea de vânzare, se corectează conturile 411 «Clienți», 707 «Venituri din vânzarea mărfurilor», 607 «Cheltuieli privind mărfurile» și 371 «Mărfuri». [...] Tratamentul TVA în aceste situații este cel prevăzut de legislația în domeniu."
— OMFP nr. 1.802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate), pct. 330 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce înseamnă, concret, „a corecta" o stornare completă:

- Stornarea unei vânzări de marfă (returnată de client sau facturată greșit) trebuie să corecteze **patru conturi simultan**: creanța față de client (411), venitul din vânzare (707), cheltuiala cu marfa vândută (607) **și stocul de marfă** (371) — nu doar primele două, legate direct de factură.
- Dacă se corectează doar 411 și 707 (partea „vizibilă" pe factură), dar se omite 607 și 371, rezultatul e o discrepanță: contabil, marfa apare vândută (scoasă din gestiune și trecută pe cheltuială), deși fizic s-a întors în depozit.
- Dacă returul se referă la o vânzare din **exercițiul financiar anterior**, corecția nu se mai face direct pe 707/607, ci prin conturile de regularizare — 418 „Clienți — facturi de întocmit" sau 408 „Furnizori — facturi nesosite", după caz — și se reflectă în situațiile financiare ale exercițiului la care se raportează, dacă sumele sunt cunoscute la data bilanțului.
- Aceeași regulă se aplică identic returului de **produse finite** vândute, cu conturile corespunzătoare (7015, 711, 345 în loc de 707, -, 371).
- Tratamentul TVA aferent returului urmează regulile specifice din Codul fiscal (ajustarea bazei de impozitare la reduceri/anulări de livrări), separat de corecția contabilă a stocului.

## Ce se greșește în practică

- Se stornează doar factura (411 și 707), fără să se reintroducă marfa în gestiune prin conturile 607 și 371, lăsând stocul contabil mai mic decât cel fizic real.
- Se tratează la fel returul dintr-un exercițiu financiar precedent ca pe unul din exercițiul curent, fără să se treacă prin conturile de regularizare (418/408) cerute pentru returul din perioade anterioare.
- Se omite ajustarea corespunzătoare a TVA aferente returului, tratând stornarea doar ca o corecție de valoare netă, fără TVA.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are o funcție de stornare a facturilor (`core/facturi_api.py`, funcția `storneaza`), care generează o factură de corecție cu cantități negative, referențiată la factura originală. Modulul de gestiune a stocurilor (`core/stocuri.py`) descarcă gestiunea pe baza facturilor de vânzare emise. Aplicația **nu garantează automat** că stornarea unei facturi de vânzare readuce marfa în stoc — dacă factura de stornare nu e emisă și contată corect, cu liniile corespunzătoare de marfă, corectarea stocului rămâne o verificare manuală a contabilului, separată de simpla anulare a facturii.

[iConta.eu](/)
