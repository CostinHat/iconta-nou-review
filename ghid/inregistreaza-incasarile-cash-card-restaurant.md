---
title: Cum se înregistrează încasările cash și card ale unui restaurant?
description: Din Raportul Z zilnic, numerarul și cardul se despart pe conturi diferite — 5311 pentru cash, 5125 pentru card — pe baza nomenclatorului de tip de plată al casei de marcat.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se înregistrează încasările cash și card ale unui restaurant?

Numerarul și cardul dintr-o zi de vânzare la restaurant nu se contabilizează la fel — sunt conturi diferite de trezorerie, iar Raportul Z le separă deja pe categorii.

## Temeiul legal

::: ghid-temei
„conțin datele aferente fiecărei zile fiscale încheiate" — OPANAF 146/2018 (norma metodologică pentru aplicarea OUG 28/1999), care descrie structura raportului Z, inclusiv secțiunea de plăți pe tip (`<pl tipP valPl/>`)
:::

## Cum se împart sumele

Casa de marcat fiscală înregistrează, pentru fiecare vânzare, tipul de plată folosit — nomenclator standard (card, numerar, tichete de masă, bonuri valorice, voucher etc.). Raportul Z centralizează aceste sume pe tip de plată la finalul zilei.

Din acest total, aplicația generează nota contabilă:

- **numerar → `5311 = 707`** (casa în lei = venituri din vânzarea mărfurilor/serviciilor)
- **card (și orice altă plată electronică din nomenclator: tichete, vouchere etc.) → `5125 = 707`** (conturi la bănci = venituri)

TVA colectată aferentă se închide separat, pe fiecare cotă: `707 = 4427`.

Dacă înregistrarea se face prin **import al fișierului AMEF**, separarea numerar/card citește direct din secțiunea de plăți `<pl>` a fișierului — orice tip de plată apărut efectiv acolo, nu doar cele două categorii. Dacă se face **manual**, formularul are doar două câmpuri — Numerar și Card — deci orice altă plată electronică (tichete de masă, de exemplu) trebuie inclusă manual în totalul de „Card", pentru că nu are câmp propriu.

## Ce se greșește în practică

Amestecarea celor două conturi de trezorerie — încasarea prin card e trecută greșit pe 5311, iar diferența de casă fizică nu se mai potrivește la sfârșitul zilei. A doua greșeală: la introducerea manuală, uitarea de a aduna tichetele de masă/vouchere-le în totalul „Card", ceea ce lasă numerar+card sub totalul real vândut pe zi.

## Ce face iConta.eu

Formularul manual al Raportului Z are câmpuri separate pentru numerar și card, cu validare automată că suma lor egalează totalul pe cote de TVA. Importul de fișier AMEF preia direct din raport orice tip de plată din nomenclator, nu doar cele două categorii principale — util dacă restaurantul acceptă și tichete de masă sau vouchere prin POS.

[iConta.eu](/)
