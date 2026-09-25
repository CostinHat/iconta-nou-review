---
title: "Ce trebuie să fac după ce primesc aviz de inspecție fiscală?"
description: "Ce conține avizul de inspecție fiscală, când se comunică și ce obligații are contribuabilul din momentul primirii lui, potrivit Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce trebuie să fac după ce primesc aviz de inspecție fiscală?

Avizul de inspecție fiscală este documentul prin care ANAF anunță formal declanșarea unui control și perioadele/obligațiile fiscale care urmează să fie verificate. Primirea lui deschide un interval de pregătire — nu o obligație de a răspunde imediat, dar nici de ignorat.

## Temeiul legal

::: ghid-temei
„ART. 122 Avizul de inspecție fiscală [...]
(2) Avizul de inspecție fiscală se comunică contribuabilului/plătitorului, înainte de începerea inspecției fiscale, astfel: [...]
(4) Avizul de inspecție fiscală se comunică la începerea inspecției fiscale în următoarele situații: [...] c) pentru extinderea inspecției fiscale la perioade sau creanțe fiscale, altele decât cele cuprinse în avizul de inspecție fiscală inițial;
(7) Avizul de inspecție fiscală cuprinde: [...]"
— Legea 207/2015, art. 122 alin. (2), (4), (7) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce trebuie să faci concret, din momentul primirii avizului:

- **Verifică perioadele și obligațiile fiscale menționate** — avizul indică exact ce se controlează (de exemplu impozit pe profit 2023-2025, TVA 2024); inspecția nu se poate extinde peste ce e comunicat, decât printr-un nou aviz (excepția fiind extinderea în timpul controlului, conform alin. (4) lit. c)).
- **Pregătește documentele justificative** pentru perioadele vizate — facturi, contracte, registre contabile, extrase de cont — organizate astfel încât să poată fi puse la dispoziția echipei de inspecție la data programată.
- **Verifică organul fiscal care a emis avizul și data programată** de începere a inspecției, menționate obligatoriu în conținutul avizului.
- **Ai dreptul de a solicita, motivat, amânarea** datei de începere a inspecției, dacă ai un motiv obiectiv (de exemplu, contabilul e indisponibil), dar cererea trebuie formulată în scris și justificată.
- Din momentul comunicării avizului, organul fiscal are obligația generală de a te înștiința asupra drepturilor și obligațiilor care îți revin în procedură (art. 7 alin. (1) din Legea 207/2015).

## Ce se greșește în practică

- Se ignoră avizul până în ziua controlului, fără nicio pregătire prealabilă a documentelor pentru perioada vizată — timpul dintre comunicare și începerea efectivă a inspecției e exact intervalul destinat pregătirii.
- Se presupune că inspecția se poate extinde liber la orice perioadă, fără a verifica dacă extinderea a fost comunicată corect, conform art. 122 alin. (4) lit. c).
- Se răspunde solicitărilor inspectorilor fără a păstra o evidență proprie a documentelor puse la dispoziție și a datelor la care au fost solicitate — o evidență utilă mai ales dacă urmează o eventuală contestație a raportului de inspecție.

## Ce face iConta.eu

iConta.eu urmărește obligațiile declarative curente ale firmei (termene de depunere, scadențe, coerența între declarații) prin modulul de control fiscal (`core/control_fiscal_api.py`, `core/alerte_control_fiscal.py`), care generează alerte pentru riscuri de neconformitate curentă. La data acestui ghid, aplicația **nu are o funcționalitate dedicată pentru gestionarea unei inspecții fiscale în curs** — nu înregistrează primirea unui aviz de inspecție, nu urmărește termenele acestuia și nu organizează documentele solicitate de echipa de inspecție. Pregătirea pentru control rămâne un proces manual, sprijinit doar de evidența contabilă generală ținută corect în aplicație.

[iConta.eu](/)
