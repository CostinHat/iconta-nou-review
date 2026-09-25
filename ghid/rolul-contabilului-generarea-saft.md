---
title: "Rolul contabilului în generarea SAF-T"
description: "Ce date trebuie să confirme contabilul înainte de depunerea D406/SAF-T, și cum diferă rolul lui de cel al programului care generează efectiv fișierul XML."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Rolul contabilului în generarea SAF-T

SAF-T (declarația D406) nu e o declarație pe care contabilul o completează câmp cu câmp, ca un formular clasic — e un export structurat al datelor deja existente în contabilitatea firmei (jurnal, parteneri, stocuri, active). Rolul contabilului nu e să „scrie" SAF-T, ci să se asigure că datele sursă din contabilitate sunt complete și corecte, pentru că orice eroare din contabilitatea curentă se propagă direct în fișier.

## Temeiul legal

::: ghid-temei
„ORDIN Nr. 1783/2021 din 4 noiembrie 2021 privind natura informațiilor pe care contribuabilul/plătitorul trebuie să le declare prin fișierul standard de control fiscal, modelul de raportare, procedura și condițiile de transmitere, precum și termenele de transmitere și data/datele de la care categoriile de contribuabili/plătitori sunt obligate să transmită fișierul standard de control fiscal"
— OPANAF 1783/2021 (titlul ordinului), anexa nr. 5 modificată prin OPANAF 407/2025 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt, anaf_surse/opanaf_407_2025_saft_d406.txt)
:::

Ce revine concret contabilului, în fluxul de generare a SAF-T:

- **Verificarea datelor de partener**: fiecare linie de tranzacție trebuie să identifice corect clientul sau furnizorul (CustomerID/SupplierID) sau, pentru liniile fără partener extern, codul propriu al firmei — o eroare de partener la sursă (de exemplu o factură fără CUI corect introdus) produce o linie SAF-T invalidă sau, mai rău, una validă dar cu date greșite.
- **Verificarea completitudinii jurnalului**: toate tranzacțiile lunii (facturi, note contabile, mișcări de stoc) trebuie să fie efectiv înregistrate în contabilitate înainte de generarea fișierului — SAF-T exportă ce există în jurnal, nu ce ar trebui să existe.
- **Confirmarea perioadei fără mișcări**: dacă o lună nu are tranzacții, fișierul se depune „pe zero", cu secțiunile relevante goale, nu se fabrică tranzacții artificiale pentru a evita un fișier gol.
- **Reconcilierea periodică** dintre soldurile din SAF-T și balanța de verificare a lunii — o divergență semnalează, de regulă, o eroare de mapare a datelor sursă, nu o eroare a formatului XML în sine.

## Ce se greșește în practică

- Se tratează SAF-T ca pe o declarație separată, completată manual, în loc de un export al datelor deja înregistrate — ceea ce duce la introducerea dublă a acaleiași informații, cu risc de neconcordanță între contabilitate și fișier.
- Se ignoră erorile de la sursă (facturi cu partener incomplet sau incorect) presupunând că „validatorul" le va semnala automat, în loc să se corecteze datele înainte de generare — unele erori de mapare pot fi raportate de validator pe o secțiune ulterioară celei unde e cauza reală.
- Se generează un fișier gol sau se omite depunerea pentru o lună fără activitate, în loc să se depună „pe zero", explicit, cu secțiunile fără mișcări marcate corect.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează efectiv fișierul SAF-T (D406) din datele contabile deja înregistrate în aplicație — jurnal, parteneri, active, stocuri (`core/d406.py` și modulele conexe: `d406_active.py`, `d406_stocuri.py`, `d406_reconciliere.py`). Aplicația construiește structura XML conform cerințelor OPANAF, inclusiv identificarea corectă a partenerilor pe fiecare linie de tranzacție și generarea fișierului „pe zero" pentru lunile fără mișcări — dar corectitudinea datelor sursă (facturi introduse complet și corect) rămâne responsabilitatea contabilului care le introduce.

[iConta.eu](/)
