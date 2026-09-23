---
title: Cum se verifică dacă o cheltuială aparține șantierului corect?
description: Verificarea se face prin raportul „realizat pe centru" din iConta.eu — se compară centrul selectat pe fiecare linie de notă manuală cu șantierul căruia îi aparține real cheltuiala, iar linia „nealocat" arată ce nu a fost încă etichetat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se verifică dacă o cheltuială aparține șantierului corect?

Cu mai multe șantiere active, greșeala de a eticheta o cheltuială pe centrul de cost greșit (sau de a o lăsa neetichetată) denaturează costul fiecărei lucrări. Verificarea corectitudinii se face la nivel de linie de notă, nu la nivel de notă întreagă.

## Temeiul legal

::: ghid-temei
„(6) Persoanele prevăzute la alin. (1)-(4) organizează și conduc, după caz, și contabilitatea de gestiune, potrivit reglementărilor elaborate în acest sens."

— Legea contabilității nr. 82/1991, art. 1 alin. (6)
:::

Alocarea corectă a cheltuielilor pe centre de cost este contabilitate de gestiune — o disciplină internă, fără o procedură de verificare impusă de lege. Corectitudinea ei se verifică prin instrumentele de raportare disponibile, nu printr-o obligație normativă.

## Ce se greșește în practică

- Se verifică doar antetul notei, nu liniile ei — centrul de cost se atribuie pe fiecare linie în parte, deci o notă poate avea unele linii corect alocate și altele nu, sau alocate pe centre diferite.
- Se consideră „nealocat" ca fiind mereu o eroare — pentru notele generate automat (amortizare, salarii, bancă, facturi), lipsa centrului de cost este comportamentul implicit al aplicației, nu un bug; alocarea trebuie făcută manual, dacă e nevoie.
- Se ignoră raportul „realizat pe centru" ca instrument de control — el arată exact ce a fost alocat pe fiecare centru și cât a rămas nealocat, pentru orice interval de date.

## Ce face iConta.eu

La editarea unei note manuale din Registrul jurnal, fiecare linie are un selector propriu de centru de cost, populat din nomenclatorul de centre active ale firmei — verificarea corectitudinii se face vizual, linie cu linie, la momentul înregistrării sau al revizuirii notei.

Pentru o verificare la nivel de ansamblu, raportul „realizat pe centru" adună, pentru orice interval `de`–`pana` ales, cheltuielile (clasa 6) și veniturile (clasa 7) din notele validate, grupate pe fiecare centru — inclusiv centrele fără activitate în perioadă, afișate cu zero — plus o linie separată „nealocat", cu sumele din note validate care nu poartă niciun centru. Compararea sumei „nealocat" cu așteptările contabilului (de exemplu: „ar trebui să fie aproape zero, pentru că am alocat tot") este modul practic de a detecta cheltuieli scăpate sau alocate greșit.

[iConta.eu](/)
