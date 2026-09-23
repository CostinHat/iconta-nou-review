---
title: Se poate corecta un bilanț deja depus?
description: Nu — regula contabilă e explicită. Situațiile financiare ale unui exercițiu deja depus nu se modifică; eroarea se corectează în exercițiul curent.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se poate corecta un bilanț deja depus?

Răspunsul scurt este nu — și nu e o limitare a vreunei aplicații, ci regula contabilă însăși.

## Temeiul legal

::: ghid-temei
„Corectarea erorilor aferente exercițiilor financiare precedente nu determină modificarea situațiilor financiare ale acelor exerciții."
— OMFP 1802/2014, pct. 68 (1)
:::

Odată depuse, situațiile financiare ale unui exercițiu încheiat rămân neschimbate. Când se descoperă ulterior o eroare aferentă acelui exercițiu, ea nu se corectează prin modificarea/redepunerea bilanțului respectiv, ci prin înregistrarea corecției **în exercițiul financiar curent**, pe seama rezultatului reportat (contul 117) — stornare în roșu sau înregistrare inversă, conform politicii contabile adoptate de firmă (pct. 69).

Situația e diferită doar dacă eroarea privește exercițiul financiar curent, care nu a fost încă închis și raportat: atunci corecția se face direct pe contul de profit și pierdere al anului curent (pct. 67 (1)).

## Ce se greșește în practică

- Se caută, în van, o funcție de „bilanț rectificativ" pentru S1005/S1003, prin analogie cu declarațiile fiscale rectificative (de exemplu D101 sau D300) — un asemenea mecanism nu există pentru situațiile financiare anuale.
- Se presupune că orice corecție ulterioară anulează validitatea bilanțului deja depus — de fapt bilanțul rămâne valabil ca atare; doar rezultatul reportat al anilor următori reflectă corecția.

## Ce face iConta.eu

Motorul de bilanț (`core/bilant.py`, `core/bilant_api.py`) nu conține nicio funcție de rectificare a unui S1005/S1003 deja generat — aplicația respectă, prin absența acestei funcții, exact regula legală de mai sus: nu se „redeschide" un exercițiu deja raportat. Corecția se înregistrează ca notă contabilă obișnuită în exercițiul curent (pe 117, dacă privește un an anterior), iar bilanțul viitor al firmei o va reflecta automat, la următoarea generare din balanța actualizată.

[iConta.eu](/)
