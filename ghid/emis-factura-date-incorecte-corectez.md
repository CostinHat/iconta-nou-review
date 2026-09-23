---
title: "Am emis o factură cu date incorecte: cum corectez"
description: "Cum se corectează o factură emisă cu date greșite, prin stornarea ei și emiterea unui document nou, nu prin editarea directă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am emis o factură cu date incorecte: cum corectez

Dacă ai emis o factură cu date incorecte (sumă, cotă de TVA, cantitate, client etc.), corecția corectă — mai ales dacă factura a fost deja contabilizată — este stornarea ei, urmată, dacă e cazul, de emiterea unei facturi noi și corecte.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"
— OMFP 1802/2014, pct. 69
:::

Stornarea nu modifică factura inițială — ea rămâne așa cum a fost emisă — ci adaugă un document nou, cu efect economic invers, care anulează valoarea celei greșite. Corecția propriu-zisă a datelor (sumă corectă, cotă corectă etc.) se face prin emiterea unei facturi noi, separate.

## Ce se greșește în practică

Greșeala tipică este să se editeze direct factura greșită după ce a fost deja contabilizată sau transmisă, ca și cum simpla modificare a datelor ar rezolva problema. Nu este cazul: „Corecția unei facturi contabilizate se face prin STORNO — un al doilea document, care își produce propria notă", iar o notă de contare nu poate fi „dezlegată" — mesajul de refuz al aplicației este explicit: „Dacă factura trebuie corectată, se stornează."

## Ce face iConta.eu

Pentru o factură emisă (care nu este ea însăși un document de stornare), butonul „Stornează" din ecranul de facturi creează automat un document nou de corecție:

- cu cantități **negative** (copie a liniilor originalului, negate);
- cu un **număr nou**, din aceeași serie;
- legat de factura originală printr-o referință internă, astfel încât ambele documente rămân vizibile în evidență;
- păstrând **cursul valutar al facturii originale**, nu cursul zilei stornării, astfel încât corecția să anuleze exact suma în lei a facturii inițiale;
- copiind **clasificarea fiscală a originalului** (relevantă, de exemplu, pentru declarațiile ulterioare).

Aplicația avertizează explicit înainte de acțiune: „Se creează o factură de stornare […] (valori negative, document contabil). Acțiunea nu poate fi anulată." Cota de TVA folosită pe documentul de stornare este aceeași cu cea a facturii originale — nu se recalculează la data stornării. După stornare, dacă tranzacția a fost totuși reală doar cu date greșite, emiți o factură nouă, cu datele corecte.

[iConta.eu](/)
