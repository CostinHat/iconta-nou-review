---
title: "Cum se înregistrează plata salariilor prin bancă?"
description: iConta.eu generează fișierul de plată SEPA pentru salarii, dar nu înregistrează contabil plata efectivă — nota contabilă a statului acoperă doar obligațiile declarate la D112, nu ieșirea banilor din bancă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se înregistrează plata salariilor prin bancă?

Răspunsul scurt și corect: **nu se „înregistrează" automat, în sensul unei note contabile de plată**. iConta.eu generează fișierul de plată către bancă (formatul SEPA folosit pentru transferul NET-ului salarial), dar contabilizarea ieșirii efective de bani din contul bancar (contul 5121) nu face parte din acest flux.

## Temeiul legal

::: ghid-temei
„Salariul se plăteşte în bani cel puţin o dată pe lună, la data stabilită în contractul individual de muncă, în contractul colectiv de muncă aplicabil sau în regulamentul intern, după caz." — Legea nr. 53/2003 (Codul muncii), art. 161 alin. (1)

„Plata salariului se poate efectua prin virament într-un cont bancar, în cazul în care aceasta modalitate este prevăzută în contractul colectiv de muncă aplicabil." — Legea nr. 53/2003 (Codul muncii), art. 161 alin. (2)
:::

Legea nu impune o „înregistrare" specială pentru plata prin bancă — doar condiționează dreptul angajatorului de a plăti prin virament de existența unei prevederi în contractul colectiv de muncă aplicabil.

## Ce înseamnă, concret, în evidența contabilă

Contabilizarea completă a unui salariu plătit prin bancă presupune două operațiuni distincte:

1. **Nota contabilă a obligațiilor** — generată din statul de plată: cheltuiala salarială și datoriile față de bugetul de stat/bugetele sociale (impozit, CAS, CASS, CAM), pe conturile de cheltuieli în corespondență cu 421/444/4315/4316/436.
2. **Achitarea efectivă a netului** — ieșirea de bani din bancă, înregistrată prin nota **421 = 5121**.

Prima operațiune are un corespondent direct în aplicație. A doua — nu. Fișierul de plată SEPA generat pentru transferul netului salarial pe card este un **document de execuție bancară** (un ordin de virament în format standardizat ISO 20022), nu o operațiune contabilă. El nu produce, singur, nicio notă contabilă.

## Ce se greșește în practică

Se presupune că, odată descărcat și transmis băncii fișierul de plată, aplicația a „înregistrat" automat și plata în evidența contabilă. Nu e cazul: nota 421=5121 trebuie introdusă manual, pe baza extrasului de cont care confirmă efectiv debitarea.

## Ce face iConta.eu

iConta.eu generează fișierul de plată SEPA (format pain.001.001.03) pentru NET-ul salarial al angajaților cu IBAN valid, pe baza statului de plată calculat în aplicație. Fișierul se validează automat pe schema XSD oficială înainte de a fi pus la dispoziție pentru descărcare/transmitere către bancă. Nota contabilă generată separat pentru statul de plată acoperă doar obligațiile declarate la D112 (impozit, CAS, CASS, CAM) — nu conține și contrapartida de trezorerie pentru achitarea netului. Înregistrarea ieșirii de bani din bancă (421=5121) rămâne, la acest moment, în afara acestui flux.

[iConta.eu](/)
