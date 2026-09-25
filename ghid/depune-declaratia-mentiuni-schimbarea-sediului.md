---
title: "Când se depune declarația de mențiuni pentru schimbarea sediului"
description: "Termenul legal pentru anunțarea la ANAF a modificărilor ulterioare datelor din declarația de înregistrare fiscală, inclusiv schimbarea sediului social."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când se depune declarația de mențiuni pentru schimbarea sediului

Schimbarea sediului unei firme trece prin două proceduri separate: înregistrarea noii adrese la Oficiul Registrului Comerțului (ONRC) și, distinct, anunțarea modificării la ANAF, prin declarație de mențiuni. Multă lume se oprește la prima și uită de a doua, deși termenul pentru cea de-a doua e strict și sancționat.

## Temeiul legal

```
::: ghid-temei
„(1) Modificările ulterioare ale datelor din declarația de înregistrare fiscală trebuie aduse la cunoștință organului fiscal central, în termen de 15 zile de la data producerii acestora, prin completarea și depunerea declarației de mențiuni."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 88 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::
```

Ce înseamnă asta concret pentru schimbarea sediului:

- **Termenul este de 15 zile** de la data la care se produce efectiv modificarea (de regulă, data înregistrării noului sediu la ONRC), nu de la data deciziei asociaților sau a semnării actului adițional.
- Obligația vizează **orice** modificare a datelor din declarația de înregistrare fiscală — sediul e doar unul dintre exemple; aceleași 15 zile se aplică schimbării obiectului de activitate, a reprezentantului legal, a datelor de contact etc.
- Nedepunerea declarației de mențiuni în termen este contravenție, sancționată potrivit art. 336 alin. (1) lit. a) din Codul de procedură fiscală (aceeași faptă care acoperă și nedepunerea declarațiilor de înregistrare sau de radiere).
- Declarația de mențiuni către ANAF este **separată** de mențiunea depusă la ONRC pentru actualizarea registrului comerțului — una nu o înlocuiește pe cealaltă.

## Ce se greșește în practică

- Se depune mențiunea la ONRC și se consideră procesul încheiat, fără să se mai anunțe și ANAF — deși vectorul fiscal al firmei (adresa de corespondență, administrația fiscală competentă) rămâne neactualizat.
- Se calculează termenul de 15 zile de la data hotărârii asociaților, nu de la data la care modificarea a devenit efectivă (înregistrarea la ONRC).
- Se presupune că schimbarea sediului în cadrul aceleiași localități nu necesită mențiune la ANAF — obligația de declarare se aplică oricărei modificări a datelor de înregistrare, indiferent de distanța mutării.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu generează și nu depune automat declarația de mențiuni** către ANAF — nu a fost găsit în `core/` un modul dedicat acestui proces. Aplicația păstrează datele de identificare ale firmei (inclusiv sediul) în profilul acesteia, pentru a fi folosite corect pe facturi și declarații, dar actualizarea efectivă a sediului la ONRC și transmiterea declarației de mențiuni către ANAF rămân, la acest moment, proceduri realizate separat, prin mijloacele obișnuite.

[iConta.eu](/)
