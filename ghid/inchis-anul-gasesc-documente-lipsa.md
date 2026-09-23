---
title: "Ce fac dacă am închis anul și găsesc documente lipsă?"
description: "Cele două căi disponibile când descoperi, după închiderea anului, că un document nu a fost înregistrat: contarea la data descoperirii sau redeschiderea motivată a perioadei."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce fac dacă am închis anul și găsesc documente lipsă?

Descoperirea unui document lipsă după ce ai închis (blocat) lunile unui an nu te obligă automat să redeschizi perioada — ai două căi, iar aplicația le tratează diferit.

## Temeiul legal

::: ghid-temei
„Erorile constatate după depunerea situaţiilor financiare anuale se corectează la data constatării lor, potrivit reglementărilor contabile emise de instituţiile prevăzute la art. 4 alin. (1) şi (3), după caz." — Legea nr. 82/1991 (Legea contabilității), art. 36^2
:::

Pe acest principiu se bazează calea implicită de rezolvare descrisă mai jos: nu redeschizi perioada veche, ci înregistrezi documentul la data la care l-ai găsit.

## Ce se greșește în practică

- Se cere redeschiderea întregii perioade pentru un singur document lipsă, deși există o cale mai simplă (contarea la data descoperirii) care nu presupune deblocarea lunii vechi.
- Se redeschide o perioadă fără motiv consemnat — aplicația nu permite asta: deblocarea cere obligatoriu un motiv, nu se face „prin ștergere".
- Se presupune că orice document lipsă poate fi introdus retroactiv, direct pe data lui reală, indiferent dacă luna respectivă e blocată — orice încercare de scriere pe o lună închisă e respinsă indiferent de sursă (interfață, import, cron, rețetar).

## Ce face iConta.eu

**Calea 1 — contarea la data descoperirii.** Motorul de contare acceptă parametrul `data_nota`: dacă luna documentului e blocată, nota poate fi scrisă la data la care ai găsit documentul, în luna curentă deschisă, cu o mențiune care documentează legătura cu data reală a documentului. Nu necesită redeschiderea perioadei vechi.

**Calea 2 — redeschiderea perioadei.** Dacă totuși e nevoie ca documentul să apară exact în luna lui de origine, administratorul firmei poate redeschide acea lună — dar deblocarea cere obligatoriu un motiv consemnat, pe temeiul citat direct în aplicație: „OMFP 1802/2014 — o perioadă închisă se redeschide ca act, nu prin ștergere." Fiecare blocare și deblocare e păstrată în istoricul firmei (cine, când, cu ce motiv).

Indiferent de cale, orice scriere pe o lună încă blocată e respinsă la nivel de bază de date, cu mesajul: „Perioada e blocată (luna închisă). Cere-i administratorului cabinetului să o redeschidă sau înregistrează în luna curentă." — deci nu există un mod „accidental" de a ocoli blocarea.

[iConta.eu](/)
