---
title: Cum știu sigur dacă firma mea e plătitoare de impozit pe profit în 2026
description: Statusul se verifică în câmpul „Regim fiscal" din Vector fiscal — dar câmpul reflectă ce a fost salvat, nu o interogare live la ANAF.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum știu sigur dacă firma mea e plătitoare de impozit pe profit în 2026

„Sigur" înseamnă, în acest caz, două lucruri diferite: ce arată vectorul salvat în aplicație și dacă acea valoare reflectă corect condițiile legale reale — cele două nu sunt automat identice.

## Temeiul legal

::: ghid-temei
**Art. 47 alin. (1) CF** (condiții cumulative de eligibilitate pentru regimul micro — dacă oricare nu e îndeplinită, firma e la profit): venituri sub echivalentul a 100.000 euro (lit. c), depunerea la termen a situațiilor financiare anuale, condiția salariatului (lit. g), condiția „o singură microîntreprindere" la asociați cu peste 25% la firme legate. Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, linia 6095 și următoarele.

**Art. 52 alin. (1) CF**: obligația de trecere la profit „începând cu trimestrul în care s-a depășit" plafonul de venituri, dacă depășirea are loc în cursul anului. Sursă: `anaf_surse/cod_fiscal_227_2015_consolidat.txt`, linia 6414.
:::

Prima verificare, imediată: câmpul „Regim fiscal" din ecranul Date firmă → Vector fiscal, care poate fi „micro" sau „profit". Dacă e gol, vectorul nu e completat (`completat=False`), iar declarațiile dependente de regim apar gri în semafor, nu implicit „micro" sau „profit" — necompletarea nu are o valoare implicită tacită.

A doua verificare, mai profundă: dacă valoarea salvată reflectă corect realitatea legală. Aplicația nu validează automat condițiile de eligibilitate din art. 47 (venituri, situații financiare, salariat, întreprinderi legate) — dacă firma a depășit plafonul în cursul anului fără ca cineva să actualizeze manual vectorul, câmpul poate arăta în continuare „micro", deși legal firma datorează deja impozit pe profit de la trimestrul depășirii.

Pentru certitudine completă, singura cale e verificarea manuală, periodică, a tuturor condițiilor din art. 47 față de situația reală a firmei — vectorul din aplicație e o evidență a ceea ce s-a introdus, nu o sursă de adevăr legal independentă.

## Ce se greșește în practică

- Se consideră valoarea din Vector fiscal drept adevăr absolut, fără verificare periodică a condițiilor legale reale de eligibilitate.
- Se confundă „vector necompletat" (gri, cauza necunoscută) cu „firmă la micro implicit" — necompletarea nu are valoare implicită.
- Se presupune că iConta compară automat câmpul cu ANAF pentru regimul fiscal — comparația live cu ANAF există doar pentru statutul de plătitor TVA, nu pentru regimul micro/profit.

## Ce face iConta.eu

Endpoint-ul `GET /tenants/{id}/vector` întoarce vectorul salvat, plus flag-ul `completat = bool(regim_fiscal)` — dacă regimul nu a fost setat, semaforul de declarații arată explicit cauza, nu un implicit „micro". Comparația roșu/verde/gri față de ANAF există doar pentru statutul de plătitor TVA, nu pentru regimul de impozitare micro/profit — pentru acesta din urmă, nu există nicio verificare automată împotriva condițiilor legale din art. 47, responsabilitatea fiind integral a contabilului.

[iConta.eu](/)
