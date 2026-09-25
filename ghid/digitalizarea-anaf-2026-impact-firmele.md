---
title: "Digitalizarea ANAF 2026: impact pe firmele mici"
description: "Extinderea RO e-Factura, SAF-T (D406) și digitalizarea proceselor ANAF — ce înseamnă pentru firmele mici obligațiile declarative electronice, conform actelor normative în vigoare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Digitalizarea ANAF 2026: impact pe firmele mici

Digitalizarea fiscală din ultimii ani nu a fost un proces uniform — a intrat treptat, prin acte normative separate, în viața firmelor mici: mai întâi facturarea electronică obligatorie, apoi extinderea SAF-T. În 2026, majoritatea firmelor mici se află deja sub incidența ambelor obligații.

## Temeiul legal

::: ghid-temei
„Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura [...]."
— Legea 227/2015 (Codul fiscal), art. 319 alin. (1^1), introdus prin Legea 296/2023 (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

Două fire separate de digitalizare afectează direct firmele mici:

- **RO e-Factura** — pentru operațiunile B2B între persoane impozabile stabilite în România, singurul document cu valoare legală de factură e cel transmis prin sistemul național (art. 319 alin. 1^1 Cod fiscal, introdus de Legea 296/2023); obligația a intrat treptat în vigoare pentru toate categoriile de operatori economici, indiferent de mărime;
- **SAF-T (declarația D406)** — fișierul standard de control fiscal, reglementat prin OPANAF 1783/2021, cu extinderea calendarului de raportare treptat de la marii contribuabili către restul categoriilor, inclusiv firmele mici, potrivit termenelor stabilite ulterior prin ordine ale președintelui ANAF;
- pentru firmele mici, ambele obligații înseamnă, în esență, aceeași cerință structurală: datele contabile și de facturare trebuie să existe într-un **format electronic standardizat, verificabil automat**, nu doar în registre interne sau facturi pe hârtie/PDF.

## Ce se greșește în practică

- Se tratează RO e-Factura și SAF-T ca fiind aceeași obligație, sau se presupune că depunerea uneia acoperă cerințele celeilalte — sunt două sisteme distincte, cu structuri XML, termene și scop diferite (facturare, respectiv control fiscal integrat).
- Se amână pregătirea pentru SAF-T pe motiv că „firma e prea mică", fără verificarea calendarului efectiv de extindere pentru categoria firmei, publicat prin ordine ale președintelui ANAF ulterioare OPANAF 1783/2021.
- Se subestimează efortul de adaptare a evidenței contabile interne (conturi, coduri, parteneri) la cerințele de nomenclator ale acestor declarații electronice — ele cer o structurare a datelor mai riguroasă decât cea suficientă doar pentru un bilanț anual.

## Ce face iConta.eu

iConta.eu are module dedicate ambelor direcții de digitalizare: transmiterea și primirea facturilor prin RO e-Factura (`core/efactura_send.py`, `core/efactura_trimitere.py`, `core/efactura_import.py`) și generarea declarației SAF-T/D406 (`core/d406.py`, `core/d406_reconciliere.py`), construită pe schema XSD oficială publicată de ANAF. Aplicația automatizează astfel exact cele două obligații structurale ale digitalizării fiscale relevante pentru firmele mici, reducând nevoia de intervenție manuală asupra formatelor electronice.

[iConta.eu](/)
