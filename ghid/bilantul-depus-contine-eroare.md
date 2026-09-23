---
title: Ce fac dacă bilanțul depus conține o eroare?
description: Ce se corectează pe rezultatul curent și ce nu mai poate fi „retușat" pe un bilanț deja depus — regula din OMFP 1802/2014 pentru corectarea erorilor contabile.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă bilanțul depus conține o eroare?

Prima întrebare care contează: eroarea descoperită ține de exercițiul financiar curent sau de un exercițiu financiar deja închis și raportat? Răspunsul diferă complet.

## Temeiul legal

::: ghid-temei
„Corectarea erorilor aferente exercițiului financiar curent se efectuează pe seama contului de profit și pierdere."
— OMFP 1802/2014, pct. 67 (1)

„Corectarea erorilor aferente exercițiilor financiare precedente nu determină modificarea situațiilor financiare ale acelor exerciții."
— OMFP 1802/2014, pct. 68 (1)
:::

Din aceste două reguli rezultă tratamentul practic:

- **Eroare din anul curent** (bilanțul nu a fost încă depus, sau vorbim de o eroare descoperită înainte de închiderea exercițiului) → se corectează direct, pe seama contului de profit și pierdere al anului curent.
- **Eroare dintr-un exercițiu anterior deja depus** → situațiile financiare deja depuse pentru acel an **nu se modifică**. Corecția se face în exercițiul curent, prin rezultatul reportat (contul 117), nu prin redepunerea bilanțului vechi.

Stornarea propriu-zisă se face fie prin stornare în roșu, fie prin înregistrare inversă (stornare în negru), în funcție de politica contabilă a firmei (pct. 69).

## Ce se greșește în practică

- Se încearcă „redepunerea" bilanțului anului trecut, ca și cum ar exista o procedură de rectificare a formularului S1005/S1003 deja transmis — o astfel de procedură nu există.
- Se corectează eroarea unui an anterior direct pe contul de profit și pierdere al anului curent, în loc de rezultatul reportat (117), umflând sau diminuând artificial profitul/pierderea anului curent.

## Ce face iConta.eu

Trebuie spus deschis: motorul de generare a bilanțului din iConta.eu (`core/bilant.py`, `core/bilant_api.py`) **nu are nicio funcție de corectare sau rectificare a unui S1005/S1003 deja generat** — nu există niciun mecanism care să „redeschidă" o declarație deja produsă. Ce oferă aplicația este suportul contabil pentru tratamentul corect descris mai sus: înregistrarea notei de corecție (pe 117, pentru erorile din exerciții anterioare, sau direct pe conturile de clasa 6/7, pentru erorile din exercițiul curent), care va fi reflectată automat la următoarea generare a bilanțului din balanța actualizată.

[iConta.eu](/)
