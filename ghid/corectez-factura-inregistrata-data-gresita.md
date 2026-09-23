---
title: Cum corectez o factură înregistrată cu data greșită?
description: O dată greșită pe o factură deja introdusă nu se editează în iConta.eu. Fără notă contabilă, se șterge și se reintroduce cu data corectă. Cu notă contabilă, corecția e prin stornare (facturi emise) sau prin corecția notei, cu grija suplimentară ca luna corectă să fie deschisă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o factură înregistrată cu data greșită?

Data unei facturi contează dublu: stabilește documentul justificativ real și, implicit, luna în care intră nota ei contabilă. O dată greșită introdusă la înregistrare nu se corectează prin editare — factura, odată creată, nu are câmp de dată modificabil direct.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ." — Legea contabilității nr. 82/1991, art. 6 alin. (1)

„Corectarea erorilor se efectuează la data constatării lor." — OMFP 1802/2014, Anexa 1 – Reglementări contabile, pct. 65 alin. (2)
:::

Data reală a documentului nu se schimbă retroactiv — dacă a fost introdusă greșit, ea se corectează, dar corecția însăși e o operațiune nouă, datată la momentul la care greșeala a fost observată.

## Cum corectez în iConta.eu

- **Factura nu are încă notă contabilă** → se șterge și se reintroduce cu data corectă. Nota ei nouă va prelua automat această dată corectă.
- **Factura are notă contabilă** (a fost deja contată, eventual chiar pe o lună diferită de cea corectă) → ștergerea e refuzată; corecția se face prin stornare (pentru facturi emise, `storneaza()` creează factura de stornare) și introducerea facturii noi, cu data reală.
- Un caz frecvent la corectarea datei: data corectă cade într-o lună deja închisă administrativ. Poarta de perioadă blochează contarea pe acea lună — nota facturii noi (sau de stornare) nu poate primi decât o dată dintr-o lună deschisă; dacă data reală a documentului rămâne pe o lună închisă, nota se datează la data constatării/corectării, cu mențiunea explicită a datei reale în descriere.
- Dacă doar nota contabilă are data greșită, iar factura însăși e corectă, corecția e mai simplă: cât timp nota e ciornă, data ei se editează direct; dacă e deja validată, corecția e prin notă de stornare (pct. 69).

## Ce se greșește în practică

- Se presupune că data facturii se poate „muta" liber, ca un câmp editabil — nu există, pentru o factură deja introdusă, o astfel de operație.
- Se forțează data reală a documentului pe nota de contare, deși luna respectivă e închisă — aplicația refuză, iar corecția rămâne incompletă până se alege data corectă de înregistrare.
- Se ignoră diferența dintre „data facturii" (a documentului justificativ) și „data notei" (a înregistrării contabile) — cele două pot diferi legitim, dar diferența trebuie explicată în descrierea notei, nu ascunsă.

## Ce face iConta.eu

Data unei facturi deja introduse nu se editează direct. Fără notă contabilă, factura se șterge și se reintroduce cu data reală. Cu notă contabilă, corecția urmează calea de stornare, iar dacă luna corectă e închisă, nota nouă se datează la momentul corecției, cu motivul consemnat explicit — data reală a documentului nu se pierde, doar înregistrarea contabilă poartă data la care corecția a fost făcută.

[iConta.eu](/)
