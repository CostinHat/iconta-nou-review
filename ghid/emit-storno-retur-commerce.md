---
title: Cum emit storno pentru un retur din e-commerce?
description: Factura de stornare pentru un retur din e-commerce e un document nou, cu cantități negative, care copiază numărul, cursul valutar și clasificarea fiscală ale facturii originale — nu o factură recalculată la data returului.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum emit storno pentru un retur din e-commerce?

Un retur dintr-un magazin online se traduce contabil printr-o factură de stornare, care corectează exact factura inițială de vânzare — nu o factură nouă, independentă, ci una construită să anuleze precis prima operațiune.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"

— OMFP 1802/2014, reglementări contabile consolidate, pct. 69
:::

Practic, stornarea unui retur din e-commerce presupune un document nou cu următoarele caracteristici: cantitățile de pe liniile facturii originale sunt copiate cu semn negativ; documentul primește un număr propriu, rezervat din aceeași serie ca originalul; păstrează cursul valutar al facturii inițiale, nu cursul zilei de retur — altfel stornarea n-ar anula exact suma în lei plătită inițial; și copiază integral clasificarea fiscală a originalului (regim de TVA, taxare inversă dacă e cazul, categoria de operațiune) — pentru ca declarațiile ulterioare să vadă returul exact ca pe o „oglindă" a vânzării, nu ca pe o operațiune nouă, neclasificabilă.

## Ce se greșește în practică

- Se emite o factură nouă „de corecție", cu propriile ei cote și clasificări introduse manual, în loc de o stornare care copiază automat datele originalului — riscul e o clasificare fiscală diferită de a vânzării inițiale, care rupe corespondența în declarațiile de TVA.
- Se folosește cursul valutar al zilei de retur în loc de cel al facturii inițiale, la vânzările în valută — suma în lei nu se mai anulează exact.
- Se confundă anularea (o factură netransmisă, ale cărei operațiuni nu au fost înregistrate în contabilitate) cu stornarea (o factură deja intrată în circuit, corectată printr-un document nou) — sunt situații fiscal diferite.

## Ce face iConta.eu

Funcția de stornare din iConta.eu creează automat documentul de corecție pornind strict de la factura originală: copiază liniile cu cantități negative, rezervă un număr nou din aceeași serie, păstrează cursul valutar al originalului și copiază integral clasificarea fiscală a acestuia (țară terț, taxare inversă, categorie de operațiune intracomunitară, plătitor de TVA etc.). Descrierea fiecărei linii pe documentul de stornare începe cu „STORNO:", urmată de descrierea originală, pentru trasabilitate.

[iConta.eu](/)
