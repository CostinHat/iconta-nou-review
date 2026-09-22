---
title: Ce fac dacă am stins factura greșită la încasare?
description: Documentul justificativ trebuie să reflecte operațiunea reală, deci o alocare greșită trebuie corectată; sistemul permite suprascrierea alocării propuse de motor înainte de contare, dar o linie deja contată nu mai poate fi recontată automat — corecția devine manuală.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce fac dacă am stins factura greșită la încasare?

Se întâmplă: motorul de matching sau utilizatorul alocă o încasare pe altă factură decât cea corectă a partenerului, mai ales când există mai multe facturi deschise cu solduri apropiate. Ce se poate face depinde de un singur lucru — dacă linia a fost deja contată sau nu.

## Temeiul legal

::: ghid-temei
**Articolul 6 (1)** Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ. **(2)** Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz.
:::

## Înainte sau după contare — diferența contează

Cât timp o linie de extras nu a fost încă trecută prin contare (`conteaza`), alocarea sugerată automat de motor (potrivire exactă, combo sau FIFO) poate fi suprascrisă manual, prin parametrul `alocari` — utilizatorul poate alege explicit altă factură sau altă combinație de facturi decât cea propusă de sistem, înainte de a genera înregistrarea contabilă.

Odată ce o linie a fost contată, `core/reconciliere_api.py` blochează explicit re-contarea aceleiași linii (`status='contat'`) — motorul nu oferă un mecanism automat de anulare sau realocare a unei linii deja contabilizate. Practic, dacă suma a fost deja stinsă pe factura greșită și înregistrarea contabilă a fost generată, corectarea nu se face prin re-rularea motorului de matching, ci printr-o corecție contabilă manuală, în afara fluxului automatizat de matching descris aici.

Onest spus: dosarul de cod verificat pentru F073 nu documentează un flux specific de "anulare + realocare" pentru o linie deja contată — acest caz iese din aria motorului pur de matching. Tratarea corectă a corecției (stornare, notă de corecție etc.) e o decizie contabilă care nu ține de logica de matching descrisă aici.

## Ce se greșește în practică

- Se încearcă re-importul aceleiași linii de extras, sperând că motorul o va realoca automat — sistemul blochează recontarea unei linii deja marcate `status='contat'`.
- Se corectează doar factura afectată vizual (în evidența facturilor), fără să se atingă și înregistrarea contabilă deja generată din alocarea greșită — soldurile rămân inconsecvente.
- Se confundă alocarea greșită pe o factură a aceluiași partener cu o compensare între o factură emisă și una primită de la același CUI — F073 nu automatizează acest al doilea caz, indiferent de statusul liniei.
- Se lasă eroarea nesemnalată, considerând-o "minoră", deși ea afectează soldul real al ambelor facturi implicate (cea greșit stinsă și cea rămasă efectiv neîncasată).

## Ce face iConta.eu

Înainte de contare, `conteaza` din `core/reconciliere_api.py` acceptă parametrul `alocari`, care permite suprascrierea alocărilor sugerate de motorul de matching — util exact pentru a corecta o propunere greșită înainte de a genera înregistrarea contabilă. Fiecare alocare contată generează o înregistrare separată (`status='ciorna'`, `sursa='banca'`), legată de `factura_id`.

Pentru facturi deschise ale aceluiași partener pe direcții diferite (o factură emisă și una primită de la același CUI), motorul nu oferă compensare încrucișată automată — `facturi_partener` filtrează strict pe o singură direcție per linie de extras. Odată contată o linie, sistemul nu oferă recontare automată; corectarea unei alocări greșite deja contate rămâne un pas manual.

[iConta.eu](/)
