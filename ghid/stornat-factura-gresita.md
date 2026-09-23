---
title: "Ce fac dacă am stornat factura greșită?"
description: "Ce prevede aplicația când chiar documentul de stornare a fost introdus greșit și de ce corecția lui nu are, momentan, o cale dedicată în interfață."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am stornat factura greșită?

E o situație diferită de „am stornat o factură care nu trebuia corectată" — aici problema este că **documentul de stornare în sine** a fost introdus greșit (de exemplu ai stornat altă factură decât cea vizată, sau ai apăsat din greșeală butonul). Iată ce se știe, verificat direct în cod, despre această situație.

## Temeiul legal

::: ghid-temei
„Dacă factura trebuie corectată, se stornează."
— mesaj de refuz al aplicației la încercarea de a desface o notă de contare (regula generală vine din OMFP 1802/2014, pct. 69: stornarea se face prin corectare cu semn minus sau prin înregistrare inversă a operațiunii inițiale, nu prin ștergere)
:::

Regula generală de corecție în contabilitate este stornarea, nu ștergerea sau editarea unei operațiuni deja înregistrate. Această regulă se aplică și notei de contare a unei facturi de stornare greșite: nota nu se poate „desface", ea se corectează tot prin stornare.

## Ce se greșește în practică

Greșeala este să se creadă că orice document — inclusiv unul de stornare — poate fi el însuși stornat din interfață, la fel de simplu ca o factură obișnuită. Nu este întotdeauna cazul, iar încercarea de a edita sau șterge nota de contare a stornării greșite nu este calea corectă: o notă de contare nu se poate „dezlega" din aplicație.

## Ce face iConta.eu

Aici trebuie spus onest ce arată codul verificat: butonul „Stornează" din ecranul de facturi apare doar pe o factură emisă care **nu este ea însăși** un document de stornare. Cu alte cuvinte, **un document de stornare nu poate fi el însuși stornat din interfața aplicației** — momentan nu există o cale dedicată de UI pentru „stornarea stornării".

Mecanismul general de creare a unei stornări (document nou, cantități negative, referință la original) se poate aplica tehnic oricărei facturi emise, dar interfața nu expune această opțiune pentru un document care este el însuși un storno. În această situație, corectarea documentului de stornare greșit nu are, la acest moment, o cale dedicată în interfața standard — rămâne o decizie de la caz la caz (de exemplu o notă de corecție separată în jurnal), nu un flux acoperit integral de aplicație.

[iConta.eu](/)
