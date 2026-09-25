---
title: "e-Factura B2B 2026: obligații și termen de transmitere"
description: "Obligația de transmitere prin RO e-Factura în relația dintre firme și termenul legal de 5 zile lucrătoare, valabile în 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# e-Factura B2B 2026: obligații și termen de transmitere

Obligativitatea RO e-Factura în relația dintre firme (B2B) nu este nouă în 2026, dar termenul de transmitere a fost recent redefinit, iar în 2026 persoanele care se identifică prin CNP au și un termen explicit de înscriere în registrul obligatoriu.

## Temeiul legal

::: ghid-temei
„În relaţia comercială B2B, între persoane impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015 [...], emitentul facturii electronice are obligaţia de transmitere a acesteia către destinatar utilizând sistemul naţional privind factura electronică RO e-Factura [...]"
— OUG nr. 115/2023, care a introdus obligativitatea B2B în OUG nr. 120/2021 (sursă: anaf_surse/oug_115_2023_consolidat.txt)

„Termenul-limită pentru transmiterea facturilor în sistemul naţional privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015 [...]"
— OUG nr. 120/2021, art. 10 alin. (7), astfel cum a fost modificat prin OUG nr. 89/2025 (sursă: anaf_surse/oug_89_2025.txt)
:::

Pentru 2026, două lucruri contează practic:

- **Obligația B2B rămâne generală**, pentru orice persoană impozabilă stabilită în România care emite facturi către altă persoană impozabilă, cu excepția bonurilor fiscale care îndeplinesc condițiile unei facturi simplificate și a facturilor pentru livrări intracomunitare către beneficiari cu cod de TVA din alt stat membru.
- **Termenul de transmitere este de 5 zile lucrătoare** — o schimbare față de forma anterioară a legii, care vorbea despre 5 zile calendaristice; calculul zilelor lucrătoare se face conform Regulamentului (CEE, Euratom) nr. 1182/71.
- În plus, OUG 89/2025 introduce, pentru furnizorii/prestatorii care se identifică fiscal prin cod numeric personal (adică persoanele fizice cu activitate economică, inclusiv PFA), obligația de a solicita **înscrierea în Registrul RO e-Factura obligatoriu** — cei care au început activitatea înainte de 15 ianuarie 2026 au avut obligația să solicite înscrierea până la acea dată, fiind înscriși automat cu data de 15 ianuarie 2026.

## Ce se greșește în practică

- Se folosește vechea regulă de 5 zile calendaristice, aplicabilă înainte de OUG 89/2025, în loc de 5 zile lucrătoare — diferența contează mai ales în preajma weekend-urilor sau a sărbătorilor legale.
- Se ignoră a doua limită a termenului (legată de data-limită de emitere din Codul fiscal), calculând doar de la data efectivă a emiterii.
- Se presupune că doar firmele (SRL, SA etc.) intră sub obligația B2B — persoanele fizice cu activitate economică independentă, identificate prin CNP, intră și ele, cu regula suplimentară de înscriere în registru introdusă pentru 2026.

## Ce face iConta.eu

iConta.eu generează și transmite facturile B2B prin RO e-Factura din modulul `core/efactura_send.py` (declanșat prin `core/efactura_trimitere.py`), folosind conectorul OAuth2 al firmei. Aplicația nu calculează, la acest moment, un contor vizibil al termenului de 5 zile lucrătoare rămase pentru fiecare factură nesincronizată — verificat direct în cod, transmiterea propriu-zisă se face **doar** la inițiativa utilizatorului: nu există un job programat care să urce automat facturile netransmise către SPV (`core/spv_poll.py` e documentat explicit ca „jumătatea de PRIMIRE a propriului send" — interoghează starea trimiterilor deja făcute, nu inițiază trimiteri noi). Respectarea termenului legal de 5 zile lucrătoare rămâne, deci, responsabilitatea contribuabilului. Starea fiecărei trimiteri deja făcute (în așteptare, acceptată, respinsă) este urmărită automat prin `core/spv_poll.py`.

[iConta.eu](/)
