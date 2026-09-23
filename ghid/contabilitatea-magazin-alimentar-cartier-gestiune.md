---
title: "Contabilitatea unui magazin alimentar de cartier: gestiune"
description: "Cum se aplică metoda global-valorică (preț cu amănuntul) la gestiunea unui magazin alimentar de cartier, folosind motorul de calcul al iConta.eu."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitatea unui magazin alimentar de cartier: gestiune

Un magazin alimentar de cartier este, prin natura activității, un comerț cu amănuntul — exact situația pentru care legea prevede metoda prețului cu amănuntul (global-valorică), atunci când marfa este numeroasă, cu mișcare rapidă și marje similare.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 286 alin. (8): „În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă. În această situație, costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor. Orice modificare a prețului de vânzare presupune recalcularea marjei brute."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Descrierea legală de mai sus („articole numeroase și cu mișcare rapidă, care au marje similare") corespunde exact profilului unui magazin alimentar de cartier: sute sau mii de produse diferite, rulaj rapid, pentru care urmărirea costului individual pe fiecare articol ar fi nepractică.

## Ce se greșește în practică

- Se ține evidența la cost de achiziție pe fiecare produs în parte, ceea ce devine ingerabil la un sortiment mare, în loc de metoda prețului cu amănuntul, gândită exact pentru acest caz.
- Se schimbă prețul de vânzare la stocul existent fără recalcularea marjei brute cerută explicit de ultima teză a alin. (8).
- Se calculează adaosul comercial pe fiecare vânzare, în loc de coeficientul de repartizare cumulat, calculat lunar.

## Ce face iConta.eu

Motorul de gestiune global-valorică al iConta.eu acoperă mecanismul descris mai sus: la recepția mărfii (`nir_gv`, `core/stocuri.py`), cota de TVA este obligatorie explicit pe fiecare linie sau ca parametru — aplicația nu presupune tacit o cotă implicită, tocmai pentru a evita erori la schimbarea legislației TVA. Costurile accesorii (transport, taxe) se capitalizează în costul de achiziție și se repartizează proporțional pe liniile de recepție.

Lunar, funcția `descarca_luna` calculează coeficientul de repartizare cumulat de la 1 ianuarie și propune automat, ca ciornă, nota de descărcare de gestiune (607/378/4428) — validarea rămâne manuală, în sarcina contabilului. Conform cercetării care stă la baza acestui ghid, aplicația nu are o funcție dedicată de „reprețuire" a stocului deja recepționat (`nir_gv` fixează prețul de vânzare doar la intrare); recalcularea marjei brute la o schimbare de preț, cerută de lege, rămâne o procedură contabilă manuală, nu un ecran dedicat în iConta.eu.

[iConta.eu](/)
