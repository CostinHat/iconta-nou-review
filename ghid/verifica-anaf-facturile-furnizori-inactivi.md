---
title: "Ce verifică ANAF la facturile de la furnizori inactivi?"
description: "Ce pierde firma, potrivit Codului fiscal, dacă deduce cheltuieli sau TVA pe baza unor facturi emise de un furnizor declarat inactiv, și cum se verifică acest lucru."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce verifică ANAF la facturile de la furnizori inactivi?

Un furnizor poate fi declarat inactiv de ANAF fără ca acest lucru să fie evident la prima vedere — firma nu primește o notificare automată la fiecare achiziție. Consecința reală apare abia la control, când ANAF verifică dacă printre documentele de bază ale cheltuielilor și TVA-ului deduse se află facturi emise de un contribuabil aflat, la data emiterii, în Registrul contribuabililor inactivi.

## Temeiul legal

::: ghid-temei
„Nu sunt considerate cheltuieli deductibile: [...] j) cheltuielile înregistrate în evidența contabilă, care au la bază un document emis de un contribuabil declarat inactiv conform prevederilor Codului de procedură fiscală, cu excepția celor reprezentând achiziții de bunuri efectuate în cadrul procedurii de executare silită și/sau a achizițiilor de bunuri/servicii de la persoane impozabile aflate în procedura falimentului potrivit Legii nr. 85/2014."
— Legea 227/2015, art. 25 alin. (4) lit. j) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Beneficiarii care achiziționează bunuri și/sau servicii de la persoane impozabile stabilite în România, după înscrierea acestora ca inactivi în Registrul contribuabililor inactivi/reactivați conform Codului de procedură fiscală, nu beneficiază de dreptul de deducere a cheltuielilor și a taxei pe valoarea adăugată aferente achizițiilor respective [...]"
— Legea 227/2015, art. 11 alin. (7) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce verifică, în esență, un inspector la control:

- **Data emiterii facturii** față de **perioada de inactivitate** a furnizorului, așa cum apare în Registrul contribuabililor inactivi/reactivați — nu contează dacă firma a plătit cu bună-credință, ci dacă furnizorul era, la acea dată, înscris ca inactiv.
- Dacă da, atât **cheltuiala**, cât și **TVA-ul dedus** aferente acelei facturi devin nedeductibile, cu două excepții legale: achizițiile din executare silită și achizițiile de la furnizori aflați în procedura falimentului (Legea 85/2014).
- Legea prevede și o cale de recuperare: dacă furnizorul e reactivat, beneficiarul își poate recupera dreptul de deducere — dar procedura diferă după cum inactivitatea și reactivarea cad în același an fiscal sau în ani diferiți, caz în care e nevoie de declarație rectificativă.

## Ce se greșește în practică

- Se verifică statusul furnizorului o singură dată, la începutul relației comerciale, și nu se repetă verificarea periodic — un furnizor activ la prima achiziție poate deveni inactiv ulterior, iar facturile din perioada de inactivitate rămân nedeductibile chiar dacă firma nu a fost informată.
- Se confundă „furnizor inactiv" cu „furnizor cu codul de TVA anulat" — sunt regimuri diferite, cu consecințe fiscale diferite și cu excepții diferite de recuperare a deducerii.
- Se așteaptă notificare automată de la ANAF la fiecare achiziție de la un furnizor devenit inactiv — Registrul e public, dar verificarea rămâne în sarcina cumpărătorului, nu se face din oficiu de organul fiscal la emiterea facturii.

## Ce face iConta.eu

Când se introduce sau se caută un furnizor după CUI, iConta.eu interoghează API-ul public ANAF și afișează, printre datele preluate (denumire, cod CAEN, plătitor de TVA), și statusul de inactivitate (`inactiv`, din `stare_inactiv.statusInactivi`) — vezi `core/anaf_api.py`. Aplicația **nu verifică automat, la fiecare factură înregistrată**, dacă furnizorul era inactiv exact la data emiterii facturii respective, și nu blochează sau semnalează retroactiv facturile deduse de la un furnizor care a devenit între timp inactiv. Confirmarea perioadei exacte de inactivitate față de data fiecărei facturi rămâne o verificare manuală a contabilului.

[iConta.eu](/)
