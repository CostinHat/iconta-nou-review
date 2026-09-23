---
title: Cum corectezi diferențele dintre contabilitate și extrasul bancar?
description: Cele mai frecvente cauze verificate ale diferențelor sunt liniile necontate, liniile ignorate și — cel mai riscant — reimportarea aceluiași extras, care poate crea linii duplicate.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectezi diferențele dintre contabilitate și extrasul bancar?

Când soldul din contabilitate (contul 5121) nu corespunde cu extrasul bancar, cauza se găsește de obicei printre liniile de extras care nu au ajuns corect în contabilitate — necontate, ignorate sau, cel mai riscant, importate de două ori.

## Temeiul legal

::: ghid-temei
„Disponibilitățile aflate în conturi la bănci sau la unitățile Trezoreriei Statului se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității."
— OMFP 2861/2009, pct. 29 alin. (2)
:::

::: ghid-temei
„În documentele financiar-contabile nu sunt admise ștersături, modificări sau alte asemenea procedee [...] Erorile se corectează prin tăierea cu o linie a textului sau a cifrei greșite, concomitent înscriindu-se alături textul sau cifra corectă. Corectarea se face în toate exemplarele documentului și se confirmă prin semnătura persoanei care a întocmit/corectat documentul, menționându-se și data efectuării corecturii."
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 14
:::

## Cauze verificate, în ordinea probabilității

1. **Linii necontate** — rămase „nou", „potrivit" (galben, alocare parțială) sau fără potrivire (roșu) în ecranul Bancă. Cea mai frecventă și cea mai ușor de găsit cauză: se parcurge ecranul Bancă și se contabilizează sau se alocă manual liniile rămase în lucru.
2. **Linii marcate „Ignorată"** — excluse explicit din contabilizare de un utilizator; suma lor există în extras, dar nu în 5121. De verificat dacă ignorarea a fost intenționată.
3. **Reimportarea aceluiași extras (sau a unui extras cu perioadă suprapusă)** — atenție deosebită aici: aplicația nu verifică automat dacă un fișier de extras a mai fost importat, așa că reimportarea creează linii duplicate, care pot fi alocate și contabilizate separat de liniile originale. Efectul e o dublare reală în contabilitate (venit sau cheltuială dublă, stingere dublă de sold pe facturi) fără să existe o dublare reală în bancă. Dacă se suspectează acest caz, se verifică în ecranul Bancă dacă există linii cu aceeași dată, sumă și descriere apărute de două ori.
4. **Format de extras citit greșit** — parserul de import e validat pe formatul unei bănci anume; un extras într-un format diferit poate fi interpretat incorect (sume, linii omise).

## Ce se greșește în practică

- Se reimportă extrasul „ca să fie sigur" de câte ori apare o nelămurire, fără să se verifice întâi dacă liniile lui sunt deja în ecranul Bancă — riscul de duplicare e real, aplicația nu blochează reimportarea.
- Se corectează diferența „din contabilitate", printr-o notă manuală care ajustează soldul 5121, fără să se identifice cauza reală în extras — riscul e ca diferența să reapară la luna următoare.
- Se ignoră liniile „galbene" (alocare parțială FIFO) considerându-le deja rezolvate, deși ele înseamnă că suma nu s-a potrivit exact și poate necesita verificare.

## Ce face iConta.eu

Ecranul „Bancă" arată starea fiecărei linii importate, ceea ce face liniile necontate sau ignorate ușor de găsit. iConta.eu nu verifică însă automat dacă un fișier de extras a mai fost importat — nu există un control de duplicat pe fișier, dată, sumă sau descriere — astfel încât reimportarea unui extras deja procesat rămâne o cauză reală de risc, de evitat prin verificare manuală înainte de reimport.

[iConta.eu](/)
