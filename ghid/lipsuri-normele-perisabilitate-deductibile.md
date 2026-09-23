---
title: "Lipsuri peste normele de perisabilitate: deductibile sau nu"
description: Partea de pierdere care depășește limita HG 831/2004 e nedeductibilă și, suplimentar, atrage ajustare de TVA — cu o singură excepție de la ajustarea de TVA, dacă degradarea calitativă și distrugerea sunt dovedite.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Lipsuri peste normele de perisabilitate: deductibile sau nu

Partea din pierdere care depășește coeficientul de perisabilitate al grupei de mărfuri nu mai beneficiază de deductibilitate — rămâne cheltuială nedeductibilă la impozitul pe profit. Suplimentar, aceeași depășire atrage, în regula generală, ajustarea TVA-ului dedus inițial, cu o excepție explicită pentru bunurile dovedit distruse.

## Temeiul legal

::: ghid-temei
„(1) În condițiile în care regulile privind livrarea către sine sau prestarea către sine nu se aplică, deducerea inițială se ajustează în următoarele cazuri: a) deducerea este mai mare sau mai mică decât cea pe care persoana impozabilă avea dreptul să o opereze; [...]

(2) Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă. [...]"

*(Codul fiscal — Legea nr. 227/2015, art. 304 alin. (1) lit. a) și alin. (2) lit. a))*
:::

## Cele două consecințe ale depășirii

1. **Nedeductibilitate la impozitul pe profit** — `nedeductibil = pierdere_constatată − deductibil`, unde `deductibil = min(pierdere_constatată, limita)`. Partea peste limită rămâne 607 nedeductibil, indiferent de motivul depășirii.
2. **Ajustare de TVA, cu excepție** — regula generală (art. 304 alin. (1)) cere ajustarea TVA-ului dedus, proporțional cu partea nedeductibilă (635=4426, calculată la cota aplicabilă). Excepția (alin. (2) lit. a)) elimină această ajustare doar dacă degradarea calitativă e dovedită și distrugerea efectivă e demonstrată — indiferent cât de mare e depășirea.

## Ce se greșește în practică

- Se presupune că depășirea limitei anulează automat deductibilitatea, dar fără să se verifice separat dacă se aplică excepția de TVA pentru bunuri dovedit distruse.
- Se aplică excepția de TVA doar pe baza faptului că marfa a expirat, fără dovada efectivă a distrugerii (proces-verbal, predare la eliminare).
- Se calculează ajustarea de TVA la toată valoarea pierderii, nu doar la partea nedeductibilă care depășește limita.

## Ce face iConta.eu

Motorul F066 (`core/perisabilitati.py`) generează linia de ajustare TVA (635=4426) doar dacă există parte nedeductibilă ȘI parametrul `degradare_dovedita_distrusa` nu e bifat; dacă e bifat, ajustarea nu se face, indiferent de mărimea depășirii. Decizia că degradarea și distrugerea sunt „dovedite" rămâne o evaluare a contabilului, pe baza documentelor disponibile (proces-verbal de distrugere) — aplicația nu verifică singură existența acestei dovezi.

[iConta.eu](/)
