---
title: Cum se descarcă gestiunea pentru vânzările cu bon fiscal?
description: Pentru vânzările pe bon fiscal (restaurant, comerț cu amănuntul fără factură pe fiecare vânzare), descărcarea de gestiune se face lunar, global-valoric, cu un coeficient K — nu pe fiecare bon, și nu automat din Raportul Z.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se descarcă gestiunea pentru vânzările cu bon fiscal?

Important de clarificat de la început: mecanismul de aici **nu** e cel folosit la descărcarea de gestiune pentru vânzările pe factură (care se face pe fiecare factură, cantitativ-valoric). Pentru vânzările pe bon fiscal, fără factură — tipic restaurant sau comerț cu amănuntul — descărcarea e **lunară**, pe baza unui coeficient de adaos comercial, nu per-tranzacție.

## Temeiul legal

::: ghid-temei
„În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă." — OMFP 1802/2014, pct. 286 alin. (8)
:::

## Cum funcționează

Restaurantele și comerțul cu amănuntul care vând pe bon fiscal (fără factură, fără articol identificat individual la fiecare vânzare) țin de regulă gestiunea **global-valoric** — mărfurile intră la preț de vânzare cu TVA neexigibilă (371/378/4428), iar la ieșire se aplică un coeficient de repartizare a adaosului comercial (coeficientul K), calculat cumulat de la începutul exercițiului: raportul dintre soldul contului 378 (adaos comercial) și valoarea mărfurilor la preț de vânzare (371, minus TVA neexigibilă 4428).

Descărcarea lunară aplică acest coeficient la veniturile din vânzarea mărfurilor (707) ale lunii respective, rezultând costul mărfii vândute (607) și adaosul/TVA aferente descărcate din 378/4428.

## Legătura cu Raportul Z

Pe ecranul „Raport Z" din iConta.eu, după salvarea unei note introduse **manual**, apare un buton separat „Descarcă gestiunea GV" pentru luna respectivă. **Acest buton nu apare și pe calea de import al fișierului AMEF** — dacă vânzarea zilnică a fost încărcată prin import de fișier, descărcarea de gestiune trebuie inițiată separat, din ecranul de gestiune, nu de pe ecranul Raport Z.

De asemenea, descărcarea nu e per-bon și nu e per-Z — e o operațiune lunară, care ia în calcul toate vânzările de mărfuri ale lunii (contul 707), indiferent din câte rapoarte Z provin.

## Ce se greșește în practică

Confundarea acestui mecanism cu descărcarea de gestiune de pe factură (folosită la vânzările facturate, cantitativ-valoric, per document) — sunt două metode diferite, pentru două tipuri diferite de evidență a stocurilor, și nu se aplică ambele pe aceleași mărfuri. A doua greșeală: așteptarea ca butonul de descărcare să apară automat și după importul de fișier AMEF — el apare doar după calea manuală de introducere a Raportului Z.

## Ce face iConta.eu

Butonul „Descarcă gestiunea GV" calculează coeficientul K din soldurile curente ale conturilor 378/371/4428 și generează nota ciornă de descărcare (607, cu adaosul și TVA aferente din 378/4428), pe baza veniturilor din vânzarea mărfurilor ale lunii. E disponibil doar pe fluxul de introducere manuală a Raportului Z, nu și pe fluxul de import al fișierului AMEF — dacă folosești importul, inițiază descărcarea separat, din ecranul dedicat de stocuri.

[iConta.eu](/)
