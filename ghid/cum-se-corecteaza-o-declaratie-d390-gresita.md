---
title: Cum se corectează o declarație D390 greșită?
description: Legal, corectarea se face prin depunerea unei noi declarații pentru aceeași perioadă, bifată „rectificativă", cu toate rubricile completate cu valorile corecte — iConta.eu nu generează momentan acest XML cu bifa de rectificativă activată, așa că depunerea rectificativei se face în afara aplicației.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se corectează o declarație D390 greșită?

Ai depus o D390 și ai descoperit ulterior o eroare — o operațiune omisă, o sumă greșită, un cod de țară incorect? Procedura legală e clară, dar merită spus deschis: la acest moment, aplicația nu generează automat XML-ul cu bifa de declarație rectificativă activată. Mai jos, ce prevede legea și ce poți face concret.

## Temeiul legal

::: ghid-temei
„Declarația depusă inițial se rectifică prin depunerea unei noi declarații, pe același format, bifând căsuța corespunzătoare de pe formular. În declarația rectificativă se rectifică tranzacții declarate în orice perioadă de raportare anterioară și se completează toate rubricile formularului cu datele valabile la momentul declarării, indiferent dacă acestea au mai fost declarate."

„ATENȚIE: Informațiile completate eronat în perioade de raportare anterioare nu se corectează prin înscrierea cifrei «0» la rubrica «Bază impozabilă» din declarația recapitulativă rectificativă. Se completează câte o declarație rectificativă pentru fiecare perioadă de raportare pentru care se operează rectificări."
:::

## Procedura legală corectă

Corectarea unei D390 greșite nu se face prin scăderea sau anularea diferenței în luna curentă, ci prin depunerea unei **noi declarații pentru aceeași perioadă** (aceeași lună calendaristică) în care s-a produs eroarea, bifată explicit „rectificativă". Regulile de completare sunt stricte:

- Se completează **toate** rubricile formularului cu valorile corecte, valabile la momentul rectificării — nu doar operațiunea greșită, chiar dacă restul rubricilor au fost deja declarate corect anterior.
- Nu se corectează o eroare punând cifra „0" la baza impozabilă a operațiunii greșite — asta nu anulează informația greșită deja transmisă, doar o completează incorect a doua oară.
- Dacă erorile privesc mai multe perioade de raportare, se depune câte o declarație rectificativă separată pentru fiecare lună afectată, nu una singură care cumulează mai multe luni.

::: ghid-exemplu
O firmă a raportat greșit codul de țară al unui partener în D390 pentru luna mai. Corectarea corectă înseamnă: se depune o nouă D390 pentru luna mai, bifată „rectificativă", cu toate operațiunile din acea lună completate cu datele corecte (inclusiv cele care fuseseră deja corecte inițial) — nu doar o linie cu diferența sau cu „0" la operațiunea greșită.
:::

## Ce se greșește în practică

- Se încearcă „anularea" operațiunii greșite prin înscrierea cifrei 0 la baza impozabilă în declarația următoare — procedura interzice explicit acest lucru.
- Se raportează corecția în luna curentă, în loc să se depună o rectificativă pentru luna în care a apărut de fapt eroarea.
- Se completează în declarația rectificativă doar operațiunea greșită, omițând restul rubricilor care trebuie repetate cu valorile valabile la momentul rectificării.
- Se presupune că bifa de „rectificativă" se activează automat din aplicație la o nouă generare pentru aceeași lună — la acest moment, nu se întâmplă.

## Ce face iConta.eu

Câmpul `d_rec` (bifa „declarație rectificativă") este **hardcodat la valoarea 0** în generarea XML a declarației D390, fără parametru de suprascriere — spre deosebire de alte module ale aplicației (D104, D106, D107, D108, D110), care citesc o valoare configurabilă pentru acest câmp. Practic, aplicația nu are, momentan, o cale de a genera XML-ul unei D390 cu bifa de rectificativă activată.

Dacă descoperi o eroare într-o D390 deja depusă, procedura legală de mai sus (declarație nouă, pentru aceeași perioadă, bifată rectificativă, cu toate rubricile completate) rămâne valabilă și trebuie urmată, dar bifarea propriu-zisă a rectificativei nu poate fi generată momentan din iConta.eu — verifică varianta de completare oferită direct pe portalul ANAF pentru acest caz specific.

[iConta.eu](/)
