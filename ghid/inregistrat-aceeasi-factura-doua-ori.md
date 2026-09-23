---
title: "Ce fac dacă am înregistrat aceeași factură de două ori?"
description: "Ce se întâmplă când o factură ajunge dublată în evidență și cum se corectează, fără ștergere, o factură deja contabilizată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am înregistrat aceeași factură de două ori?

Dacă aceeași factură a ajuns înregistrată de două ori, una dintre cele două înregistrări trebuie eliminată din evidența contabilă. Regula de bază: **odată ce o factură a fost contabilizată (are notă de contare generată), ea nu se mai șterge** — corecția se face printr-un document nou.

## Temeiul legal

::: ghid-temei
„69. — Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (**stornare în roșu**), fie prin înregistrarea inversă a acesteia (**stornare în negru**), în funcție de politica contabilă și programele informatice […]"
— OMFP 1802/2014, pct. 69
:::

Corectarea unei operațiuni deja înregistrată în contabilitate se face prin stornare, nu prin ștergerea înregistrării inițiale. Acest principiu se aplică direct și cazului facturii duplicate: dacă factura „în plus" a fost deja contabilizată, ea rămâne în evidență ca document, iar efectul ei economic se anulează printr-o factură de stornare.

## Ce se greșește în practică

Greșeala tipică este să se încerce ștergerea directă a facturii duplicate, ca și cum nu ar fi existat niciodată. Odată ce o factură are notă de contare generată, ștergerea ei este blocată — corecția corectă a unei facturi contabilizate se face „prin STORNO — un al doilea document, care își produce propria notă", nu prin eliminarea facturii sau a notei din evidență.

O altă greșeală este să se creadă că a doua trecere prin motorul de contare al aceleiași facturi produce o a doua notă, „dublând" astfel eroarea contabil. Nu este cazul: a doua chemare a contării pe o factură deja contată este tratată ca operațiune fără efect (`deja_contata`), nu ca eroare și nu generează o a doua notă.

## Ce face iConta.eu

Pentru o factură deja contabilizată, aplicația nu permite ștergerea directă a documentului — corecția se realizează prin stornarea facturii care nu trebuia emisă/înregistrată, ceea ce generează un document nou, cu valori negative, legat de original. Dacă apelezi din nou funcția de contare pe o factură deja contată, aceasta recunoaște situația și nu creează o notă suplimentară.

Dosarul de cercetare nu identifică în cod o funcție dedicată de „detectare a facturilor duplicate" — decizia că o factură este într-adevăr un duplicat și trebuie stornată rămâne la latitudinea utilizatorului.

[iConta.eu](/)
