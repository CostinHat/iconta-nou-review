---
title: Cum verific dacă am respectat toate termenele lunii trecute
description: Semaforul de conformare fiscală nu arată doar ce urmează — marchează roșu, cu motiv, orice declarație a cărei scadență a trecut deja fără o depunere confirmată.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific dacă am respectat toate termenele lunii trecute

Verificarea retrospectivă — „am depus tot ce trebuia luna trecută?" — folosește același mecanism ca verificarea curentă: semaforul compară, pentru fiecare declarație și fiecare perioadă, termenul legal cu ce a fost efectiv confirmat ca depus. Diferența e doar unde te uiți: pastila roșie arată exact restanțele deja scadente, indiferent din ce lună provin.

## Temeiul legal

::: ghid-temei
„Persoanele fizice și juridice care au calitatea de angajatori sau sunt asimilate acestora [...] sunt obligate să depună lunar, până la data de 25 inclusiv a lunii următoare celei pentru care se plătesc veniturile, Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate."

*(Codul fiscal — Legea nr. 227/2015, art. 147 alin. (1), pentru D112 — un exemplu al celor 9 declarații verificate retrospectiv de semafor)*
:::

## Cum citești verificarea retrospectivă

Starea **roșie** din semafor nu apare doar pentru luna curentă — apare pentru orice perioadă trecută al cărei termen a fost depășit fără o confirmare de depunere înregistrată, indiferent cât de veche e perioada. Dai clic pe firmă pentru detaliu: fiecare declarație restantă apare cu perioada exactă la care se referă („T3 2026", „august 2026" etc.) și cu motivul verdictului.

Starea **gri** (nu se poate verifica) poate apărea și pentru perioade trecute, dacă informația din profilul firmei necesară pentru a decide aplicabilitatea (regim fiscal, statut de TVA) lipsește sau lipsea la momentul respectiv — nu înseamnă că declarația a fost depusă, ci că semaforul nu are date suficiente pentru verdict.

## Ce se greșește în practică

- Se verifică doar starea curentă a firmei, fără să se deschidă detaliul pe firmă pentru a vedea dacă există restanțe din lunile anterioare, ascunse în spatele unei stări generale „de urmărit".
- Se presupune că o restanță „veche" nu mai contează pentru control, pentru că a trecut ceva timp de la termen — semaforul nu are o dată de expirare pentru restanțe; ele rămân vizibile până la confirmarea depunerii.

## Ce face iConta.eu

Funcția `obligatii_datorate()` din modulul F022 (`core/control_fiscal_api.py`) evaluează, la fiecare accesare a ecranului, toate perioadele din trecut ale firmei — nu doar luna curentă — și marchează roșu orice declarație cu termen depășit și fără depunere confirmată. Evaluarea ține cont și de existența reală a firmei/activității în perioada respectivă, astfel încât nu apar restanțe „retroactive" pentru perioade dinainte de înființare sau de prima activitate demonstrabilă.

[iConta.eu](/)
