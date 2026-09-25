---
title: "Cum se descarcă gestiunea pentru produsele finite vândute"
description: "Nota contabilă de vânzare a produselor finite conform OMFP 1802/2014: descărcarea la cost standard (711=345), TVA obligatoriu explicit și repartizarea diferențelor de preț pe contul 348."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se descarcă gestiunea pentru produsele finite vândute

Vânzarea unui produs finit înseamnă două note contabile distincte, nu una singură: nota de venit (către client) și nota de **descărcare de gestiune** (ieșirea produsului din stoc, la cost). Descărcarea se face la costul standard la care produsul a fost recepționat în 345, iar dacă firma lucrează cu diferențe de preț pe contul 348, acestea trebuie repartizate pe ieșire, nu doar pe intrare.

## Temeiul legal

::: ghid-temei
„Contul 345 «Produse finite» [...] În creditul contului 345 «Produse finite» se înregistrează: – valoarea la preț de înregistrare a produselor finite vândute și lipsurile de inventar (711); [...]"
— OMFP 1802/2014, Reglementările contabile, Planul de conturi general — funcțiunea contului 345 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Mecanismul complet, așa cum rezultă din funcțiunea conturilor 345/348/711:

- **Vânzarea propriu-zisă**: `4111 = 701` (venit din vânzarea produselor finite) + `4111 = 4427` (TVA colectată, calculată separat, nu implicit).
- **Descărcarea de gestiune**: `711 = 345`, la costul standard al cantității ieșite din stoc — nu la prețul de vânzare.
- **Dacă firma ține diferențe de preț pe 348** (diferența dintre costul efectiv de producție și costul standard folosit ca preț de înregistrare), repartizarea la ieșire se face prin coeficientul de repartizare calculat din soldurile/rulajele 348 și 345: `711 = 348` pentru diferențele nefavorabile (cost efectiv > standard) repartizate pe ieșire, sau `348 = 711` pentru cele favorabile.
- Coeficientul de repartizare (K) se calculează din soldul inițial și rulajul contului 348 raportate la soldul inițial și intrările contului 345 din perioadă — nu e o cotă fixă, se recalculează la fiecare descărcare.

## Ce se greșește în practică

- Se descarcă gestiunea la prețul de vânzare, nu la costul standard — confuzie între nota de venit (701/4427) și nota de descărcare (711/345), care sunt independente.
- **Omiterea coeficientului 348 la descărcarea gestiunii** — dacă firma ține diferențe de preț și nu le repartizează la ieșire, stocul rămas în 345 nu mai reflectă corect costul real, iar cheltuiala/venitul din diferențe se distorsionează.
- Se presupune că diferența de preț se repartizează o singură dată, la intrare, și că ieșirile ulterioare nu mai au nevoie de recalcul — funcțiunea contului 348 cere repartizare atât la intrare, cât și la ieșire.

## Ce face iConta.eu

Funcționalitatea **Producție în curs și produse finite** (ecran Operațiuni speciale → Imobilizări) generează exact acest tipar de note prin funcția `nota_vanzare` din `core/productie.py`: `4111=701` + `4111=4427` (cu cotă de TVA obligatorie — aplicația refuză explicit generarea dacă nu se dă o cotă, ca să nu rămână o valoare implicită „ruptă tăcut de lege la prima schimbare"), apoi descărcarea `711=345` la costul standard ieșit și, dacă se transmite un coeficient `coef_348`, repartizarea diferenței (`711=348`/`348=711`).

**Limită reală, de menționat onest**: ecranul de introducere a vânzării din iConta (Operațiuni speciale → Imobilizări → Producție → Vânzare + descărcare) are, la data acestui ghid, doar câmpurile preț de vânzare, cost standard ieșit și cotă de TVA — **niciun câmp pentru coeficientul de repartizare 348**, deși motorul din spate îl acceptă și îl aplică corect dacă i se dă. Rezultatul practic: din interfața curentă, orice descărcare de gestiune se înregistrează la cost standard pur, fără repartizarea diferențelor de preț — exact greșeala pe care legea (și avertismentul intern al aplicației) o semnalează ca fiind cea mai frecventă. Calculul manual al coeficientului și transmiterea lui rămân, azi, în afara ecranului standard.

[iConta.eu](/)
