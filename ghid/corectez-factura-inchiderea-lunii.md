---
title: Cum corectez o factură după închiderea lunii
description: O factură emisă nu se editează direct în iConta.eu, iar dacă luna e închisă, editarea nici n-ar fi posibilă. Corecția se face prin stornare — o factură nouă, cu cantități negative, datată în luna curentă (deschisă).
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o factură după închiderea lunii

În iConta.eu nu există un buton „editează factura" pentru o factură deja emisă. Singurele operații posibile pe o factură existentă sunt ștergerea și stornarea — indiferent dacă luna în care a fost emisă e deschisă sau închisă.

## Temeiul legal

::: ghid-temei
„Corectarea erorilor se efectuează la data constatării lor." — OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 65 alin. (2)

„Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate." — OMFP 1802/2014, Anexa 1, pct. 69
:::

Cele două puncte explică de ce corecția nu se face „înapoi", în luna facturii greșite, ci „înainte", la data la care greșeala e observată. Programul folosit (iConta.eu) aplică varianta stornării în roșu: cantități negative pe aceleași linii, nu o înregistrare inversă separată.

## Ce înseamnă practic, în iConta.eu

Pentru o factură **emisă**, corectarea are doi pași, verificați direct în cod:

1. **Ștergerea e refuzată dacă factura are notă de contare legată.** O factură emisă primește automat, la creare, o notă de contare. Odată ce nota există, `sterge_factura` refuză ștergerea și trimite explicit spre stornare — indiferent dacă luna e blocată sau nu.
2. **Stornarea creează o factură NOUĂ**, cu aceleași linii dar cu cantitatea negativă, cu un număr nou din aceeași serie, datată **azi** (`data_emitere = data de azi`) — adică întotdeauna în luna curentă, deschisă. Nota de contare aferentă stornoului urmează aceeași dată.

Consecința: **corectarea unei facturi dintr-o lună închisă nu cere deblocarea lunii respective.** Luna veche rămâne închisă și intactă; stornoul apare în luna în care ai constatat eroarea, exact cum cere pct. 65 alin. (2) de mai sus.

Dacă factura corectă trebuie reemisă cu sumă diferită, se emite o factură nouă, separată de storno, tot în luna curentă.

**Mecanismul descris mai sus se aplică facturilor emise.** Pentru o factură **primită** de la un furnizor, iConta.eu nu are o funcție de „stornare" proprie — corecția depinde de furnizor, care trebuie să emită el o factură de corecție sau de stornare.

## Ce se greșește în practică

- Se caută un buton de editare pe factura emisă și, negăsindu-l, se încearcă ștergerea și reintroducerea de la zero — ceea ce eșuează dacă factura are notă legată, și lasă un gol în numerotare dacă se forțează.
- Se presupune că un storno trebuie datat în luna facturii originale, „ca să se compenseze acolo" — stornoul se datează la data descoperirii, nu la data facturii greșite.
- Se cere deblocarea lunii închise doar pentru a corecta o factură, deși corecția prin storno nu are nevoie de ea.

## Ce face iConta.eu

Nu există rută de editare a unei facturi emise — nici pentru facturi din luna curentă, nici pentru cele din luni închise. Corecția se face exclusiv prin storno: o factură nouă, cu cantitățile negate, cu propriul număr din serie, datată la data la care se face corecția. Legătura cu factura originală (`factura_id`) rămâne înscrisă pe nota de contare, iar dacă data notei diferă de data facturii, descrierea notei consemnează explicit acest lucru — nu apare o dată „arbitrară" fără explicație. Nu se editează niciodată direct linia unei facturi emise, indiferent de starea lunii.

[iConta.eu](/)
