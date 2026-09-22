---
title: "Stornarea facturilor și TVA: cum înregistrez"
description: Stornarea unei facturi emise se înregistrează automat prin generarea unei facturi noi, cu linii negate, care produce o notă cu semn minus conform OMFP 1802/2014 pct. 69 — nu prin inversarea manuală a unei note existente; verifică însă manual exercițiul financiar și referința la factura originală.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Stornarea facturilor și TVA: cum înregistrez

Stornarea unei facturi nu înseamnă „ștergerea" unei note contabile și nici inversarea manuală, linie cu linie, a înregistrării originale. În iConta.eu, ca și în regula contabilă pe care o implementează, storno-ul e o factură nouă, ale cărei linii — negate — produc automat, prin același motor de contare, o notă cu semn minus.

## Temeiul legal

::: ghid-temei
„69. ‐ Înregistrarea stornării unei operațiuni contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roşu), fie prin înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă şi programele informatice utilizate." — OMFP 1802/2014, pct. 69

„65. ‐ (1) Erorile constatate în contabilitate se pot referi fie la exercițiul financiar curent, fie la exercițiile financiare precedente. […] 67. ‐ (1) Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere. (2) Corectarea erorilor semnificative aferente exercițiilor financiare precedente se efectuează pe seama rezultatului reportat (contul 1174 «Rezultatul reportat provenit din corectarea erorilor contabile»)." — OMFP 1802/2014, secțiunea 2.5.2, pct. 65-68

„Articolul 36^2 Erorile constatate după depunerea situațiilor financiare anuale se corectează la data constatării lor, potrivit reglementărilor contabile emise de instituțiile prevăzute la art. 4 alin. (1) și (3), după caz." — Legea contabilității nr. 82/1991, art. 36^2

„Articolul 330 Corectarea facturilor (1) […] b) […] se emite o nouă factură care trebuie să cuprindă, pe de o parte, informațiile din factura inițială, numărul și data facturii corectate, valorile cu semnul minus […]" — Cod fiscal 227/2015, art. 330

„4111. Clienți (A)" / „4427. TVA colectată (P)" / „4428. TVA neexigibilă (A/P)" — OMFP 1802/2014
:::

## O clarificare de citare, întâi de toate

Regula de stornare (semnul minus sau înregistrarea inversă) se găsește la **pct. 69 din OMFP 1802/2014** — nu la „pct. 330". „330" există ca număr de articol, dar în alt act normativ: **art. 330 din Codul fiscal**, care reglementează conținutul obligatoriu al facturii de corecție (nu tehnica de stornare contabilă). Sunt două reguli complementare, din două legi diferite — una spune „cum se scrie nota" (OMFP pct. 69), cealaltă spune „ce trebuie să conțină documentul" (Cod fiscal art. 330). Amestecarea lor sub un singur număr e o sursă frecventă de confuzie.

## Cum se înregistrează, efectiv

Stornarea unei facturi emise nu inversează o notă deja scrisă. În schimb, sistemul construiește o **factură nouă**: aceleași linii ca originalul, dar cu cantitatea negată, descrierea prefixată „STORNO: ", un număr nou din aceeași serie, creată cu data curentă (păstrând moneda, cursul și clasificarea fiscală de pe original). Pentru că nota contabilă se generează întotdeauna din liniile facturii (cantitate × preț), iar cantitatea e acum negativă, nota iese automat cu semn minus — exact mecanica de la pct. 69 — prin același drum ca orice altă factură emisă, nu printr-o funcție separată de „inversare".

TVA-ul urmează aceeași logică cu semn schimbat: dacă factura originală a avut TVA colectată pe 4427, storno-ul o reduce tot pe 4427, cu minus; dacă factura era pe regim de TVA la încasare (4428), la fel.

::: ghid-exemplu
O factură emisă de 1.000 lei bază + TVA colectată aferentă (4111 = 707 / 4111 = 4427) se stornează. Factura de storno are aceeași bază și cotă, dar cantitate negativă, deci produce automat nota 4111 = 707 (-1.000) / 4111 = 4427 (-TVA) — nu o notă separată de „anulare", ci aceeași structură de cont, cu semn minus.
:::

## Ce se greșește în practică

- Se citează „pct. 330" ca temei al mecanicii de stornare — corect e pct. 69 din OMFP 1802/2014; art. 330 e din Codul fiscal și privește conținutul facturii de corecție, nu tehnica notei contabile.
- Se lasă storno-ul să scrie automat pe conturile de venit curent (707/701/703/704), fără a verifica dacă factura originală aparține unui exercițiu financiar anterior, deja închis — caz în care corecția ar trebui să treacă prin 1174, nu direct prin venit curent.
- Se așteaptă stornare parțială (a unei singure linii sau a unei sume) — motorul actual stornează întotdeauna 100% din factură.
- Se presupune că legătura dintre storno și factura originală apare structurat în XML-ul de e-Factura — nu apare; există doar intern, în baza de date.
- Se citește codul sursă al funcției pure de storno din motorul de calcul și se crede că ea descrie mecanismul real folosit la stornare — funcția respectivă nu e apelată de nicăieri; mecanismul real construiește o factură nouă cu cantități negative, nu inversează o notă deja scrisă.

## Ce face iConta.eu

Mecanismul real de storno (`storneaza`, în modulul de orchestrare a facturilor) citește factura originală, refuză operația dacă factura nu are direcția „emisă", construiește linii noi cu cantitatea negată și descrierea prefixată „STORNO: ", rezervă un număr nou din aceeași serie și creează documentul cu data curentă, păstrând moneda/cursul/clasificarea de pe original. Nota automată se generează prin motorul obișnuit de contare (`genereaza_note` → `factura_emisa`), cu semn minus, pentru că liniile au cantitate negativă — nu printr-o funcție separată de „storno" care ar inversa o notă deja scrisă (o astfel de funcție există în codul de calcul pur, dar nu e apelată niciodată din restul aplicației). Sistemul nu verifică exercițiul financiar al facturii originale, iar stornarea e întotdeauna totală — fără opțiune de corecție parțială. Legătura cu factura originală se păstrează doar ca o coloană internă în baza de date, nu ca referință structurată în XML-ul transmis la SPV.

[iConta.eu](/)
