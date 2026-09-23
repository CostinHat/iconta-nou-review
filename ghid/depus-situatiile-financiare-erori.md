---
title: Am depus situațiile financiare cu erori
description: Ce prevede OMFP 1802/2014 pentru corectarea erorilor descoperite după depunere, și de ce corecția se face pe rezultatul reportat al anului curent, nu prin redepunerea bilanțului.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Am depus situațiile financiare cu erori

Situațiile financiare anuale au fost deja depuse la ANAF, iar acum a apărut o eroare — ce se corectează și unde se înregistrează diferența?

## Temeiul legal

::: ghid-temei
„Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere."
— OMFP 1802/2014, pct. 67 (1)

„Corectarea erorilor aferente exercițiilor financiare precedente nu determină modificarea situațiilor financiare ale acelor exerciții."
— OMFP 1802/2014, pct. 68 (1)
:::

Erorile se pot referi fie la exercițiul curent, fie la exerciții financiare precedente deja închise (pct. 65 (1)), iar tratamentul e diferit pentru fiecare caz:

- Eroare din exercițiul **curent** (nu a fost încă depus) → se corectează pe contul de profit și pierdere al anului curent.
- Eroare dintr-un exercițiu **anterior**, deja depus → situațiile financiare ale acelui an **nu se modifică**; corecția se înregistrează în exercițiul curent, prin rezultatul reportat (contul 117), prin stornare în roșu sau înregistrare inversă, conform politicii contabile a firmei (pct. 69).

## Ce se greșește în practică

- Se caută, degeaba, o opțiune de „redepunere" sau „rectificare" a bilanțului anului cu eroarea — pentru situațiile financiare anuale, spre deosebire de unele declarații fiscale, un asemenea mecanism nu există.
- Se așteaptă cu corecția până la finalul anului curent „ca să nu complice lucrurile", deși corecția pe 117 poate fi înregistrată imediat ce eroarea e descoperită.

## Ce face iConta.eu

De reținut clar: `core/bilant.py` și `core/bilant_api.py` **nu au nicio funcție de corectare/rectificare** a unui S1005/S1003 deja generat sau depus — nu există o astfel de acțiune în aplicație. Ce oferă iConta.eu este suportul contabil corect pentru situația descrisă mai sus: se înregistrează nota de corecție pe rezultatul reportat (117), pentru erorile aferente exercițiilor precedente, iar bilanțul viitor al firmei (cel al exercițiului curent) va reflecta automat corecția, la generarea din balanța actualizată — bilanțul deja depus rămâne, formal, neschimbat.

[iConta.eu](/)
