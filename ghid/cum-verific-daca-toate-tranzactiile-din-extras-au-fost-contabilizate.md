---
title: Cum verific dacă toate tranzacțiile din extras au fost contabilizate?
description: Legea cere ca fiecare operațiune să aibă document justificativ și să fie confruntată cu soldul bancar la inventariere; practic, verificarea completă presupune parcurgerea explicită a statusurilor liniilor de extras — nou, roșu, galben, contat.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum verific dacă toate tranzacțiile din extras au fost contabilizate?

La finalul lunii, o întrebare esențială e dacă vreo linie din extrasul bancar a rămas, din greșeală, neprocesată sau necontată. Răspunsul nu ține de o singură bifă, ci de parcurgerea sistematică a statusurilor pe care motorul de matching le atribuie fiecărei linii.

## Temeiul legal

::: ghid-temei
**Articolul 6 (1)** Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ.

**29. - (2)** Disponibilitățile aflate în conturi la bănci sau la unitățile Trezoreriei Statului se inventariază prin confruntarea soldurilor din extrasele de cont emise de acestea cu cele din contabilitatea entității. [...]
:::

## Statusurile de urmărit

Fiecare linie importată dintr-un extras bancar trece prin unul din statusurile atribuite de motorul de matching: "nou" înseamnă că linia a fost importată, dar încă nu a fost procesată prin matching; roșu înseamnă fără CUI detectat în descriere sau fără nicio factură deschisă a partenerului respectiv; galben înseamnă alocare parțială FIFO, care așteaptă confirmare manuală; verde înseamnă potrivire exactă găsită de motor, dar nu încă înregistrată contabil; contat înseamnă că înregistrarea contabilă a fost deja generată, iar linia e blocată la recontare.

O verificare completă înseamnă parcurgerea, în ordine, a liniilor "nou" (procesare inițială lipsă), apoi a liniilor roșii (investigare CUI/factură lipsă), apoi a liniilor galbene (confirmare alocare parțială), apoi a liniilor verzi rămase necontate (potrivite, dar neconfirmate încă prin contare) — abia după ce nu mai rămâne nicio linie în aceste patru categorii, adică toate liniile au fost efectiv trecute prin contare, se poate spune că extrasul respectiv a fost complet contabilizat. Acest proces corespunde direct cerinței legale de confruntare a soldurilor: dacă rămân linii neprocesate sau necontate, soldul din contabilitate nu poate fi confruntat corect cu extrasul bancar.

## Ce se greșește în practică

- Se verifică doar liniile verzi și galbene deja atinse, ignorând posibilitatea ca unele linii din extras să fi rămas la status "nou", neprocesate deloc.
- Se consideră extrasul "gata" după prima trecere prin matching, fără să se revină la liniile roșii rămase neinvestigate.
- Se confundă statusul galben (alocare parțială, necesită confirmare) cu statusul contat (înregistrare deja generată) — nu sunt echivalente.
- Se confundă statusul verde (potrivire exactă găsită de motor) cu statusul contat (înregistrare contabilă deja generată) — nu sunt echivalente; o linie verde e doar potrivită, nu și contabilizată, până nu trece explicit prin contare.
- Se presupune că o linie contată e automat corectă, fără verificarea faptului că alocarea sugerată de motor a fost cea potrivită.

## Ce face iConta.eu

`core/reconciliere_api.py` persistă fiecare linie de extras importată și rulează motorul de matching (`potriveste_extras`), atribuind statusul rezultat (roșu, galben sau verde, pe baza CUI-ului și a facturilor deschise disponibile). Funcțiile de listare (`lista`, `facturi_deschise_detalii`) permit vizualizarea liniilor pe status, pentru verificare sistematică.

`conteaza` contabilizează o linie o singură dată — odată setat `status='contat'`, recontarea aceleiași linii e blocată, ceea ce previne dublarea înregistrărilor. Pentru liniile roșii fără notă manuală, sistemul poate propune o sugestie de cont pe baza istoricului deja contat, fără nicio bază legală atribuită acestei sugestii — utilizatorul rămâne responsabil de validarea ei.

[iConta.eu](/)
