---
title: "Cum corectez un registru de casă cu sold greșit?"
description: "Un sold de casă greșit nu se rescrie direct — se identifică operațiunea care l-a produs și se corectează prin regula specifică ei: tăiere cu o linie, anulare de document sau stornare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez un registru de casă cu sold greșit?

Un sold de casă greșit e aproape întotdeauna un simptom, nu problema în sine — undeva în șirul de operațiuni s-a strecurat o sumă transcrisă greșit, o operațiune omisă sau una introdusă de două ori. Corectarea corectă înseamnă găsirea acelei operațiuni și tratarea ei după regula care i se aplică, nu ajustarea soldului final ca să „iasă bine".

## Temeiul legal

::: ghid-temei
„În documentele financiar-contabile nu sunt admise ștersături, modificări sau alte asemenea procedee [...] Erorile se corectează prin tăierea cu o linie a textului sau a cifrei greșite, concomitent înscriindu-se alături textul sau cifra corectă. Corectarea se face în toate exemplarele documentului și se confirmă prin semnătura persoanei care a întocmit/corectat documentul, menționându-se și data efectuării corecturii."
— OMFP nr. 2634/2015, anexa 1, pct. 14 (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

- Regula de bază e **tăierea vizibilă**, nu ștergerea: cifra greșită rămâne lizibilă, alături apare cea corectă, iar corectura se semnează și se datează. Un sold care „arată corect" pentru că a fost rescris, fără urma erorii, contrazice explicit norma.
- Dacă eroarea nu e de transcriere, ci vine dintr-un **document de casă completat greșit** (chitanță, dispoziție de plată/încasare), pct. 15 din același ordin interzice corectura acelui document — se anulează integral și se întocmește altul nou.
- Dacă suma greșită a ajuns deja **înregistrată în contabilitate** (nota contabilă generată din operațiunea de casă e postată), corectarea nu se face nici prin tăiere, nici prin ștergere, ci prin **stornare** — cu referință încrucișată între nota inițială și cea de stornare (pct. 20).

## Ce se greșește în practică

- Se modifică direct cifra soldului de la sfârșitul zilei, fără să se identifice și să se corecteze operațiunea individuală care a generat diferența.
- Se șterge o operațiune deja postată în contabilitate, în loc să se storneze — pierzând urma controlabilă a corecturii.
- Se ignoră faptul că un sold de casă „greșit" poate însemna, de fapt, un sold **negativ** rezultat dintr-o plată mai mare decât numerarul disponibil — semn că o încasare a fost omisă sau introdusă cu întârziere, nu doar o simplă eroare de scriere.
- Se presupune că orice corectare a soldului se poate face oricând, deși un document de numerar (chitanță, dispoziție) completat greșit nu se mai poate corecta odată completat — doar anulat.

## Ce face iConta.eu

În „card Casa", operațiunile de casă se introduc prin ecranul care apelează `POST /tenants/{id}/casa/operatiuni`, iar corectarea unei operațiuni greșite depinde de statusul ei: aplicația **nu are rută de editare** (nu există niciun `PUT`/`PATCH` pentru operațiunile de casă) — singura corecție posibilă e ștergerea, și doar cât timp nota contabilă legată e încă „ciornă". Odată ce nota a fost validată/postată, aplicația refuză ștergerea („nota legată e validată; nu se mai poate șterge"), consistent cu regula de mai sus — corecția reală, în acel caz, e stornarea, ca operațiune separată de contabilitate.

O limită importantă de reținut: motorul de calcul al registrului de casă din iConta.eu **nu verifică soldul rezultat** înainte de a înregistra o operațiune — nu există nicio verificare care să semnaleze sau să blocheze introducerea unei plăți mai mari decât soldul disponibil, deci un sold de casă negativ poate apărea în registru fără niciun avertisment din partea aplicației. Dacă apare un sold neașteptat, verificarea rămâne, azi, în sarcina contabilului — nu e automatizată.

[iConta.eu](/)
