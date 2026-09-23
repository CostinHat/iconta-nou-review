---
title: "Greșeala de a nu storna o factură greșită"
description: "De ce ștergerea sau editarea unei facturi deja contabilizate nu este o soluție și cum tratează aplicația această greșeală frecventă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeala de a nu storna o factură greșită

O greșeală frecventă este să se încerce „repararea" unei facturi greșite prin editare sau ștergere, în loc de stornare — mai ales dacă factura a fost deja contabilizată. Iată de ce nu funcționează și ce se întâmplă de fapt.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"
— OMFP 1802/2014, pct. 69
:::

Regula contabilă generală este clară: o operațiune deja înregistrată se corectează prin stornare (cu semn minus sau prin înregistrare inversă), nu prin modificarea sau ștergerea înregistrării inițiale.

## Ce se greșește în practică

Cele mai frecvente greșeli, verificate direct în comportamentul aplicației:

- **Se încearcă ștergerea unei facturi deja contabilizate.** Ștergerea este blocată: „Corecția unei facturi contabilizate se face prin STORNO — un al doilea document, care își produce propria notă."
- **Se încearcă „desfacerea" notei de contare**, ca și cum nota greșită ar putea fi anulată direct. Mesajul de refuz al aplicației este explicit: „Dacă factura trebuie corectată, se stornează."
- **Se lasă factura greșită necorectată**, considerând că nu are efect dacă nu mai e „activă". Nu este așa: o factură cu status „anulată" sau „stornată" nu mai generează notă contabilă nouă, dar dacă factura greșită a fost deja contabilizată, nota ei rămâne în contabilitate până când e stornată — deci lăsarea ei necorectată denaturează evidența (inclusiv, indirect, baze de calcul care pornesc din conturile de venituri/cheltuieli afectate).

## Ce face iConta.eu

Aplicația blochează activ ștergerea unei facturi contabilizate și refuzul „dezlegării" unei note de contare — ambele forțează, prin construcție, corecția pe calea corectă: factura greșită trebuie stornată. Pentru facturile emise (care nu sunt ele însele documente de stornare), butonul „Stornează" din ecranul de facturi generează automat documentul de corecție, cu avertismentul: „Se creează o factură de stornare […] (valori negative, document contabil). Acțiunea nu poate fi anulată."

[iConta.eu](/)
