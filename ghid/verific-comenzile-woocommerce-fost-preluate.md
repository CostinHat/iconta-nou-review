---
title: "Cum verific dacă toate comenzile WooCommerce au fost preluate corect?"
description: "Singurul indicator vizibil azi e un contor agregat («N importate, M deja existente») — nu o listă a comenzilor omise, iar o comandă blocantă poate opri tăcut restul rulării."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific dacă toate comenzile WooCommerce au fost preluate corect?

Cronul WooCommerce al iConta.eu rulează automat în fiecare zi, dar o întrebare legitimă rămâne: de unde știi că *toate* comenzile finalizate din magazin au ajuns, efectiv, ca facturi în contabilitate?

## Temeiul legal

Verificarea corectitudinii unui import automat e o chestiune operațională, nu una reglementată legal — nu există o normă care să impună un anumit mecanism de confirmare a importului. Răspunderea fiscală rămâne, ca la orice factură, a firmei care o emite: dacă o comandă nu a fost preluată, veniturile aferente pot rămâne, fără să fie sesizat, nedeclarate.

## Ce se greșește în practică

- Se are încredere exclusiv în mesajul afișat după o sincronizare („N facturi importate, M deja existente"), fără să se compare periodic acest total cu numărul real de comenzi finalizate din administrarea WooCommerce.
- Nu se ține cont de faptul că o singură comandă cu o problemă (de exemplu, un produs pentru care nu se poate stabili automat cota de TVA) poate opri restul comenzilor din acea rulare — la sincronizarea automată de noapte, fără nicio alertă vizibilă cuiva; la apăsarea manuală a butonului, cu un mesaj de eroare generic, care nu spune care comandă sau produs a blocat rularea.
- Se presupune că există o listă detaliată, cu fiecare comandă și rezultatul ei individual (importată/omisă/eșuată) — nu există un asemenea ecran.

## Ce face iConta.eu

Din ecranul „Magazin online", butonul **„Sincronizează acum"** rulează manual, oricând, aceeași funcție folosită și de cronul automat de la 07:30, și afișează rezultatul brut: „N facturi importate, M deja existente" — un contor agregat, nu o listă de comenzi cu detaliu individual. Acesta e singurul feedback vizibil oferit azi despre rezultatul unei rulări reușite. O limită importantă de cunoscut: dacă o comandă din listă blochează procesarea (de exemplu, cota de TVA sau contul de venit al unui produs nu pot fi stabilite automat), comenzile rămase din acea rulare **nu sunt procesate**. Efectul asupra utilizatorului diferă după cum a pornit rularea: la cronul automat de noapte, eșecul nu ajunge la nimeni — rămâne doar un mesaj tehnic în jurnalul intern al serverului; la apăsarea butonului „Sincronizează acum", ecranul afișează un mesaj de eroare (de regulă unul generic, de tipul „eroare"), dar fără să spună care comandă sau produs anume a blocat rularea. Din acest motiv, verificarea reală, azi, înseamnă compararea manuală, periodică, a numărului de comenzi finalizate din WooCommerce cu numărul de facturi apărute în iConta, nu doar citirea contorului de la ultima sincronizare.

[iConta.eu](/)
