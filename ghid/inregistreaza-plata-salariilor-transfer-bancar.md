---
title: "Cum se înregistrează plata salariilor prin transfer bancar?"
description: „Transfer bancar" și „plată prin bancă" sunt aceeași operațiune din perspectiva iConta.eu — aplicația generează fișierul SEPA de plată, nu o notă contabilă de plată.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se înregistrează plata salariilor prin transfer bancar?

Din perspectivă tehnică și legală, „transfer bancar" și „plată prin bancă" (sau „virament") desemnează aceeași operațiune — nu există o distincție reglementată separat pentru fiecare termen. Răspunsul e identic celui pentru plata „prin bancă": iConta.eu **nu înregistrează contabil** plata efectivă, ci generează doar fișierul folosit pentru executarea transferului.

## Temeiul legal

::: ghid-temei
„Salariul se plăteşte în bani cel puţin o dată pe lună, la data stabilită în contractul individual de muncă, în contractul colectiv de muncă aplicabil sau în regulamentul intern, după caz." — Legea nr. 53/2003 (Codul muncii), art. 161 alin. (1)

„Plata salariului se poate efectua prin virament într-un cont bancar, în cazul în care aceasta modalitate este prevăzută în contractul colectiv de muncă aplicabil." — Legea nr. 53/2003 (Codul muncii), art. 161 alin. (2)
:::

Termenul legal folosit de Codul muncii e „virament într-un cont bancar", condiționat de o prevedere în contractul colectiv de muncă aplicabil (art. 161 alin. 2) — „transfer bancar" e limbajul curent pentru aceeași operațiune, fără să existe o reglementare distinctă pentru unul sau altul.

## Ce înseamnă, concret, în evidența contabilă

Ca și la plata „prin bancă", contabilizarea completă presupune două operațiuni separate:

1. **Nota contabilă a obligațiilor salariale** — generată din statul de plată (cheltuială + datorii către buget: impozit, CAS, CASS, CAM).
2. **Achitarea efectivă a netului transferat** — nota **421 = 5121**, pe baza extrasului bancar care confirmă debitarea.

Fișierul de transfer bancar generat de iConta.eu pentru plata NET-ului salarial (format SEPA, ISO 20022) acoperă doar execuția tehnică a transferului — nu produce, singur, nicio notă contabilă.

## Ce se greșește în practică

Se tratează „transfer bancar" ca pe o funcționalitate diferită de „plată prin bancă/card", căutându-se un flux separat în aplicație pentru fiecare denumire. E aceeași funcționalitate: generarea fișierului de plată SEPA pentru NET-ul salarial al angajaților cu IBAN valid.

## Ce face iConta.eu

iConta.eu generează un singur tip de fișier pentru plata salariilor pe cale bancară — fișierul SEPA (pain.001.001.03), indiferent dacă operațiunea e denumită „plată prin bancă", „transfer bancar" sau „plată pe card". Fișierul include doar angajații cu IBAN validat (verificare mod-97) și e validat pe schema XSD oficială înainte de a fi disponibil pentru descărcare. Nota contabilă a statului de plată, generată separat, acoperă doar obligațiile declarate la D112, fără contrapartida de trezorerie pentru achitarea efectivă a netului — aceasta rămâne, la acest moment, o înregistrare manuală.

[iConta.eu](/)
