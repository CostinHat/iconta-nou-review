---
title: "Cum verific dacă furnizorul avea cod valid de TVA la data facturii?"
description: O verificare la ANAF arată statutul curent al firmei, nu neapărat statutul din trecut, de la data unei facturi vechi. Pentru facturile emise chiar din iConta.eu, statutul de plătitor de TVA e verificat și „înghețat" chiar la momentul emiterii.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific dacă furnizorul avea cod valid de TVA la data facturii?

Verificarea CUI-ului unui furnizor arată, de regulă, statutul lui **curent** — dar dacă vrei să știi dacă avea cod valid de TVA **la data unei facturi vechi**, ai nevoie de datele istorice ale înregistrării, nu doar de starea de azi.

## Temeiul legal

::: ghid-temei
„Registrul contribuabililor/plătitorilor" — titlul art. 91 din Legea nr. 207/2015 privind Codul de procedură fiscală
:::

Evidența oficială ANAF ținută în baza acestui registru păstrează, alături de statutul curent, și datele privind perioadele de înregistrare ca plătitor de TVA — de aceea o interogare la sursă poate distinge statutul de azi de cel valabil la o dată anterioară.

## Cum se verifică istoricul, nu doar statutul curent

Serviciul de verificare CUI interoghează ANAF și primește, printre altele, data de la care firma e (sau a fost) înregistrată ca plătitoare de TVA și perioadele de înregistrare TVA ale firmei — nu doar un simplu „da/nu" pentru momentul actual. Pe baza acestor date se poate stabili dacă, la o dată anterioară (data facturii în discuție), furnizorul avea cod valid de TVA.

## Ce se greșește în practică

- Se verifică furnizorul azi și se presupune că același statut era valabil și la data facturii vechi — o firmă își poate schimba statutul de plătitor de TVA în timp (înregistrare, radiere, reînregistrare).
- Se acceptă o factură veche cu TVA doar pentru că furnizorul e, azi, plătitor de TVA — relevantă e situația de la data facturii, nu situația curentă.
- Se ignoră perioadele de înregistrare TVA multiple ale unei firme (dacă a fost radiată și reînregistrată) și se presupune o singură perioadă continuă.

## Ce face iConta.eu

Pentru facturile emise chiar din iConta.eu, aplicația verifică statutul de plătitor de TVA al beneficiarului la momentul emiterii și îl „îngheață" pe factură — deci pentru documentele proprii, verificarea la data facturii e automată. Pentru verificarea istorică a unui furnizor extern (a avut cod valid de TVA la o dată din trecut), interogarea la ANAF prin iConta.eu întoarce inclusiv data de început a înregistrării TVA și perioadele de înregistrare cunoscute — date pe baza cărora contabilul poate stabili situația de la data facturii respective. Verificarea rămâne, în acest caz, o interpretare a datelor primite de la ANAF, nu un răspuns automat de tip „valid/nevalid la data X".

[iConta.eu](/)
