---
title: "Cum răspund unei notificări privind diferențele din declarații?"
description: "Ce este notificarea de conformare emisă de ANAF pentru riscuri fiscale identificate în declarații și ce termen ai la dispoziție ca să corectezi situația înainte de o inspecție."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum răspund unei notificări privind diferențele din declarații?

Când ANAF identifică, prin analiza de risc, diferențe sau neconcordanțe între declarațiile depuse (de exemplu între TVA declarată și alte surse de informații pe care le are fiscul), instrumentul folosit nu e o amendă directă, ci o **notificare de conformare**: firma primește în scris riscurile identificate și un termen clar pentru a-și reanaliza și, dacă e cazul, corecta declarațiile — înainte de a fi selectată pentru inspecție fiscală.

## Temeiul legal

::: ghid-temei
„(1) Pentru contribuabilii/plătitorii prezumtivi a fi selectați pentru efectuarea inspecției fiscale, organul de inspecție fiscală transmite acestora, în scris, o notificare de conformare cu privire la riscurile fiscale identificate în scopul reanalizării de către aceștia a situației fiscale și, după caz, de a depune sau de a corecta declarațiile fiscale.
(2) Prin notificare se comunică contribuabilului/plătitorului că în termen de 30 de zile de la data comunicării notificării are posibilitatea să depună sau să corecteze declarațiile fiscale. Până la expirarea acestui termen, organul de inspecție fiscală nu întreprinde nicio acțiune în vederea selectării pentru efectuarea inspecției fiscale.
(3) Depunerea sau corectarea declarațiilor fiscale de către contribuabil/plătitor nu împiedică selectarea pentru efectuarea inspecției fiscale, însă numai după împlinirea termenului prevăzut la alin. (2).
(4) După împlinirea termenului prevăzut la alin. (2) contribuabilii/plătitorii cu risc fiscal ridicat care nu au remediat riscurile fiscale pentru care au fost notificați sunt supuși obligatoriu unei inspecții fiscale sau unei verificări documentare."
— Legea 207/2015 (Codul de procedură fiscală), art. 121^1 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Termenul de răspuns este **30 de zile calendaristice** de la comunicarea notificării — în acest interval, ANAF nu poate demara selectarea pentru inspecție.
- Ai două opțiuni concrete: depui declarațiile care lipsesc sau corectezi (rectificativ) declarațiile care conțin diferențele semnalate. Notificarea nu impune o soluție anume — doar termenul.
- Corectarea declarațiilor **nu blochează** o eventuală selectare ulterioară pentru inspecție — doar o amână peste termenul de 30 de zile — dar dacă riscul rămâne neremediat după acest termen, inspecția sau verificarea documentară devine **obligatorie**, nu opțională.

## Ce se greșește în practică

- Se ignoră notificarea, considerând-o un simplu avertisment fără consecințe — de fapt, netratarea ei duce direct la inspecție fiscală sau verificare documentară obligatorie după cele 30 de zile.
- Se corectează doar declarația la care se face referire explicită în notificare, fără să se verifice dacă diferența semnalată provine dintr-o eroare mai amplă, prezentă și în alte perioade sau declarații conexe.
- Se confundă notificarea de conformare (art. 121^1, emisă înainte de inspecție, cu scop de reanalizare voluntară) cu avizul de inspecție fiscală (art. 122, care anunță o inspecție deja decisă) — cele două au regimuri și termene diferite.

## Ce face iConta.eu

Nicio funcționalitate din iConta.eu nu citește, procesează sau afișează notificările de conformare emise de ANAF — verificat direct în cod: nu există niciun modul care se conectează la acest tip de comunicare oficială. Funcționalitatea din aplicație care se apropie cel mai mult de temă, **F131 — Notificări de plată și alerte neplătnici** (`core/scadentar.py`, `core/notificari_scadenta.py`), acoperă exact opusul direcției: reamintiri trimise de firmă către **proprii clienți** pentru facturi emise neîncasate, nu notificări primite de firmă de la ANAF. Pentru diferențele reale dintre declarații și evidența contabilă, aplicația are un instrument separat, intern și proactiv — controlul încrucișat D300 vs. conturile de TVA din balanță — util tocmai ca să previi apariția unei asemenea notificări, verificând tu însuți diferențele înainte ca ANAF să le semnaleze. Răspunsul efectiv la o notificare deja primită (depunerea sau corectarea declarațiilor în cele 30 de zile) rămâne, la acest moment, un pas realizat de contabil, în afara unui flux dedicat din aplicație.

[iConta.eu](/)
