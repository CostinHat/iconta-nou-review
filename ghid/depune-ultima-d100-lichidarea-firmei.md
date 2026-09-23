---
title: "Când se depune ultima D100 la lichidarea firmei?"
description: Dacă lichidarea se deschide și se închide în același an fiscal, ultima D100 se depune până la data depunerii situațiilor financiare de lichidare; dacă firma se dizolvă fără lichidare, termenul e închiderea perioadei impozabile — nu termenul trimestrial obișnuit, de 25 ale lunii următoare.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Când se depune ultima D100 la lichidarea firmei?

Termenul obișnuit al D100 — 25 ale lunii următoare trimestrului — nu se aplică ultimei declarații a unei microîntreprinderi care se lichidează. Legea prevede un termen specific, legat de momentul depunerii situațiilor financiare de lichidare, nu de calendarul trimestrial normal.

## Temeiul legal

::: ghid-temei
„Persoanele juridice care se dizolvă cu lichidare, potrivit legii, în cursul aceluiași an în care a început lichidarea au obligația să depună declarația de impozit pe veniturile microîntreprinderilor și să plătească impozitul aferent până la data depunerii situațiilor financiare la organul fiscal competent." — Codul fiscal, art. 56 alin. (3). „Persoanele juridice care, în cursul anului fiscal, se dizolvă fără lichidare au obligația să depună declarația de impozit pe veniturile microîntreprinderilor și să plătească impozitul până la închiderea perioadei impozabile." — art. 56 alin. (4).
:::

## Cele două situații

- **Dizolvare cu lichidare, deschisă și închisă în același an fiscal** — ultima D100 (și plata impozitului aferent) se depune **până la data depunerii situațiilor financiare** de lichidare la organul fiscal, nu la termenul trimestrial standard de 25 ale lunii următoare.
- **Dizolvare fără lichidare** (de exemplu, fuziune) — declarația și plata se fac **până la închiderea perioadei impozabile**.

Textul citat vizează explicit lichidarea deschisă și închisă „în cursul aceluiași an" — dacă procedura de lichidare se întinde pe mai mulți ani fiscali, D100 continuă, pentru anii intermediari, pe calendarul trimestrial obișnuit (art. 56 alin. (1)); regula specială de mai sus se aplică declarației finale, din anul în care lichidarea chiar se închide.

## Ce se greșește în practică

- Se așteaptă termenul trimestrial obișnuit (25 a lunii următoare) pentru ultima D100, deși legea leagă termenul de data depunerii situațiilor financiare de lichidare, care poate fi mai devreme sau mai târziu.
- Se confundă „dizolvare cu lichidare" cu „dizolvare fără lichidare" — cele două au termene diferite (data situațiilor financiare de lichidare, respectiv închiderea perioadei impozabile).
- Se presupune că, dacă ultimul trimestru de activitate are venituri zero, nu mai e nevoie de nicio declarație — obligația de depunere ține de încheierea perioadei/procedurii, nu de existența unui impozit efectiv de plată.

## Ce face iConta.eu

Motorul D100 (`core/d100.py`) calculează impozitul micro pe baza veniturilor din balanță și generează XML-ul declarației pentru trimestrul cerut — inclusiv pentru un trimestru final de lichidare, dacă rezultă o bază impozabilă pozitivă. De reținut: verificat direct în cod, aplicația **refuză** generarea XML-ului D100 dacă baza calculată e zero (nicio obligație de plată rezultată) — dacă ultimul trimestru de activitate al firmei lichidate are venituri zero, verificați separat, la organul fiscal, dacă situația concretă cere totuși o depunere „pe zero" prin alte mijloace, întrucât acest caz nu e acoperit automat de fluxul aplicației.

[iConta.eu](/)
