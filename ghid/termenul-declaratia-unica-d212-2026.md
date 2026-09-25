---
title: "Care este termenul pentru Declarația Unică D212 în 2026?"
description: "Termenul general e 25 mai a anului următor realizării veniturilor. Pentru veniturile anului 2025, termenul e 25 mai 2026, cu bonificație de 3% dacă declarația și plata se fac până la 15 aprilie 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este termenul pentru Declarația Unică D212 în 2026?

Regula generală e simplă — D212 se depune până la 25 mai inclusiv a anului următor celui de realizare a veniturilor. Pentru veniturile realizate în 2025, asta înseamnă termenul de **25 mai 2026**, dar 2026 aduce și o fereastră mai devreme, cu bonificație, pentru cine se grăbește.

## Temeiul legal

::: ghid-temei
„Declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice se completează și se depune la organul fiscal competent, pentru fiecare an fiscal, până la data de 25 mai inclusiv a anului următor celui de realizare a veniturilor."
— Codul fiscal (Legea 227/2015), art. 122 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Prin derogare de la dispozițiile art. 121 din Legea nr. 227/2015, contribuabilii persoane fizice beneficiază de o bonificație de 3% din impozitul pe venit datorat pentru veniturile realizate în anul 2025 [...] Bonificația [...] se acordă dacă [...] impozitul pe venit, contribuția de asigurări sociale și contribuția de asigurări sociale de sănătate datorate [...] se sting prin plată și/sau compensare, integral până la data 15 aprilie 2026 inclusiv; [...] declarația unică [...] se depune până la 15 aprilie 2026 inclusiv."
— OUG 8/2026, art. 8 alin. (1)-(2) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt, notă la art. 122)
:::

Ce înseamnă concret pentru 2026:

- **25 mai 2026** — termenul legal general, valabil pentru toate persoanele fizice cu obligație de depunere pentru veniturile anului 2025.
- **15 aprilie 2026** — termen opțional, mai devreme: cine depune declarația ȘI stinge integral (plată sau compensare) impozitul, CAS și CASS până la această dată beneficiază de o bonificație de 3% din impozitul pe venit datorat.
- Cine a depus deja D212 fără bonificație poate depune o rectificativă până la 15 aprilie 2026 ca să o obțină, cu aceeași condiție de plată integrală.
- Termenul de 25 mai se aplică identic și situațiilor de la art. 122 alin. (2) — începere/încetare de activitate, suspendare, modificări contractuale în cursul anului.

## Ce se greșește în practică

- Se confundă bonificația de 3% (termen 15 aprilie, condiționată de plată integrală) cu termenul legal de depunere (25 mai) — depunerea după 15 aprilie dar înainte de 25 mai nu e „întârziată", pur și simplu nu mai beneficiază de bonificație.
- Se crede că bonificația se acordă doar dacă se depune declarația, ignorând condiția cumulativă a plății integrale până la aceeași dată.
- Se aplică termenul general de 25 mai și în situații speciale unde legea cere alt moment (ex. opțiunea CASS se poate depune „oricând în cursul anului în care se optează", conform art. 180 alin. (3)).

## Ce face iConta.eu

D212 e o declarație manuală în iConta.eu (`core/d212.py`) — aplicația nu urmărește automat calendarul de scadență și nu emite notificări proprii pentru termenul de 25 mai sau pentru fereastra de bonificație de 15 aprilie. Motorul de calcul (`core/d212_engine.py`, `core/rip_api.py`) determină corect CAS, CASS și impozitul pe baza plafoanelor verificate pentru veniturile 2025 și 2026, dar decizia de a depune până la 15 aprilie pentru bonificație sau calculul valorii bonificației rămân în sarcina contabilului.

[iConta.eu](/)
