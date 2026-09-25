---
title: "Trebuie păstrat și PDF-ul sau este suficient XML-ul?"
description: "Ce document contează legal drept factură în relația B2B din România, conform Codului fiscal modificat pentru RO e-Factura, și ce rol mai are PDF-ul."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Trebuie păstrat și PDF-ul sau este suficient XML-ul?

De când transmiterea prin sistemul RO e-Factura a devenit obligatorie pentru operațiunile B2B din România, legea a răspuns explicit la întrebarea „ce document e, de fapt, factura": nu orice reprezentare vizuală a datelor, ci fișierul structurat validat de sistemul național.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura [...]."
— Legea 227/2015 (Codul fiscal), art. 319 alin. (1^1), introdus prin Legea 296/2023 (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

Coroborat cu structura tehnică a facturii electronice definită de OUG 120/2021 (art. 3 alin. 2 și art. 4 alin. 1: fișierul XML conform standardului SR EN 16931-1/RO_CIUS, primit, stocat și transmis de sistemul național RO e-Factura), rezultă:

- pentru operațiunile **B2B între persoane impozabile stabilite în România**, singurul document care are valoare legală de „factură" e fișierul XML transmis și validat prin RO e-Factura — nu reprezentarea lui vizuală;
- un PDF generat de un program de contabilitate (inclusiv de iConta.eu) e o **vizualizare** utilă pentru citire umană sau pentru arhivare informală, dar **nu înlocuiește** obligația de arhivare a fișierului XML original, cu indexul unic și semnătura electronică aplicată de Ministerul Finanțelor;
- arhivarea documentelor justificative (5 ani, calculați de la 1 iulie a anului următor încheierii exercițiului financiar în care au fost întocmite, conform art. 25 din Legea contabilității 82/1991) trebuie să vizeze fișierul XML descărcat din sistemul RO e-Factura, nu doar un export PDF intern;
- pentru facturile simplificate (art. 319 alin. 12 Cod fiscal) sau pentru operațiunile care nu intră sub incidența obligativității RO e-Factura, regula se poate aplica diferit — verificarea cazului concret rămâne necesară.

## Ce se greșește în practică

- Se arhivează doar PDF-ul emis intern de programul de contabilitate și se șterge sau se ignoră XML-ul descărcat din RO e-Factura — la un control, singurul document cu valoare de factură pentru operațiunile B2B e cel din sistemul național, nu PDF-ul.
- Se presupune că un PDF „arată la fel" cu XML-ul, deci e echivalent — conținutul structurat (coduri, referințe, sume pe linii) din XML e cel validat de sistem; un PDF generat separat poate diferi în date sau formatare fără ca discrepanța să fie vizibilă la prima vedere.
- Se ignoră faptul că regula se aplică doar între persoane impozabile stabilite în România — pentru facturile către clienți persoane fizice sau către parteneri din afara țării, regimul de arhivare poate fi diferit.

## Ce face iConta.eu

iConta.eu transmite facturile prin sistemul național RO e-Factura (`core/efactura_send.py`, `core/efactura_trimitere.py`) și importă/reconciliază facturile primite (`core/efactura_import.py`), păstrând fișierele XML aferente. Aplicația generează și o vizualizare lizibilă a facturii pentru utilizator, dar arhiva legală relevantă rămâne fișierul XML transmis/primit prin sistemul ANAF, nu reprezentarea vizuală generată intern.

[iConta.eu](/)
