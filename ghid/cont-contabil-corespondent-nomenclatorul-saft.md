---
title: Ce faci dacă un cont contabil nu are corespondent în nomenclatorul SAF-T?
description: Un cont fără mapare validă blochează validarea fișierului D406 — explicăm de unde vine nomenclatorul și ce limite are confirmarea tehnică disponibilă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce faci dacă un cont contabil nu are corespondent în nomenclatorul SAF-T?

Fișierul D406 nu acceptă conturi "libere" — fiecare cont raportat trebuie mapat la structura XML acceptată de nomenclatorul tehnic SAF-T. Când un cont din planul firmei nu are corespondent clar, validarea fișierului semnalează problema, nu o ignoră.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — cu subsecțiuni detaliate: GeneralLedgerAccounts (conturi, tip, solduri) ... — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.
:::

Important de clarificat: nomenclatoarele tehnice care descriu forma acceptată a conturilor (`d406_nomenclatoare_anaf.properties`, `d406_schema_anaf.xlsx` — sursa planurilor de conturi acceptate pe normă și a nomenclatoarelor SAF-T pentru payment method, UoM, TaxCode) **nu conțin obligații de depunere** — sunt doar structură XML, nu temei normativ de sine stătător. Temeiul obligației rămâne OPANAF 1783/2021 (structura declarației) și OPANAF 407/2025 (cine e obligat). Nomenclatorul e mijlocul tehnic prin care se respectă structura cerută, nu sursa obligației.

## Ce se greșește în practică

Greșeala tipică este să se lase contul nemapat "pentru mai târziu" și să se depună declarația oricum, sau, la polul opus, să se forțeze o mapare la un cont apropiat, dar incorect din punct de vedere al naturii economice a operațiunii — ceea ce denaturează informația raportată, chiar dacă fișierul trece validarea structurală.

## Ce face iConta.eu

Validarea fișierului D406 se face cu validatorul oficial `DUKIntegrator_AnLunaUI.jar` (integrat prin `core/duk.py`, funcția `valideaza(xml, tip, an=, luna=)`) — un cont fără corespondent valid în structura acceptată este exact genul de problemă pe care acest pas de validare este menit să o prindă înainte de depunere.

Dosarul de cercetare pentru acest ghid nu conține o descriere a unui ecran dedicat, în iConta.eu, pentru rezolvarea punctuală a unui cont nemapat — dacă întâmpinați această situație, cel mai sigur pas este verificarea planului de conturi al firmei și, dacă problema persistă, contactarea suportului iConta.eu cu exemplul concret al contului respectiv.

[iConta.eu](/)
