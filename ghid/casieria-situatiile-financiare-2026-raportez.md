---
title: "Casieria în situațiile financiare 2026: ce raportez"
description: Diferența dintre gestionarea zilnică a casei (plafoane, registru de casă) și modul în care soldul ei ajunge, la final de an, într-un singur rând din bilanț.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Casieria în situațiile financiare 2026: ce raportez

„Ce raportez din casierie la bilanț?" ține de două funcționalități diferite, cu roluri distincte: proveniența soldului de casă (gestionarea zilnică) și maparea lui în formularul de bilanț.

## Temeiul legal

::: ghid-temei
Persoanele prevăzute la art. 1 alin. (1)-(4) au obligația să întocmească situații financiare anuale.
— Legea contabilității nr. 82/1991, republicată, art. 28 alin. (1)
:::

Bilanțul trebuie să reflecte fidel patrimoniul firmei la data raportării — inclusiv soldul de casă existent la acel moment. Ce nu prevede legea contabilității este un rând distinct pentru numerar: soldul de casă se regăsește, cumulat cu celelalte disponibilități bănești, într-un singur rând al formularului.

## Ce se greșește în practică

- Se așteaptă ca soldul raportat în bilanț la disponibilități să corespundă exact cu „soldul de casă" din registrul de casă, ignorând faptul că rândul cumulează și conturile bancare, acreditivele și avansurile de trezorerie.
- Se ignoră plafoanele legale de numerar (încasări/plăți, sold de casă) pe parcursul anului, iar la 31 decembrie apare un sold de casă neobișnuit de mare, greu de justificat la un eventual control — o problemă de conformitate distinctă de raportarea în sine.

## Ce face iConta.eu

Cele două paliere sunt tratate de funcționalități separate, dar conectate:

- **Proveniența soldului** — operațiunile de casă validate în cursul anului (funcționalitatea de registru de casă și plafoane, `core/casa.py`) formează, prin rulaje, soldul final al conturilor 531/532 din balanța de verificare.
- **Raportarea în bilanț** — motorul de generare a bilanțului (`core/bilant.py`, `f10_din_balanta`) preia soldurile finale ale conturilor 5112, 512, **531, 532**, 541, 542 și le cumulează pe rândul de disponibilități al formularului F10.

Practic, dacă soldul de casă de la sfârșitul anului nu e cel așteptat în bilanț, cauza aproape sigur se află în operațiunile de casă validate în cursul anului, nu în motorul de mapare al bilanțului — verificarea corectă începe din registrul de casă, nu din ecranul de bilanț.

[iConta.eu](/)
