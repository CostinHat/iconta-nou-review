---
title: "Formatul XML pentru e-Factura: schema obligatorie 2026"
description: "Ce este RO_CIUS, actul care aprobă specificațiile tehnice ale facturii electronice folosite în sistemul RO e-Factura."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Formatul XML pentru e-Factura: schema obligatorie 2026

Facturile transmise prin sistemul RO e-Factura nu pot fi în orice format XML — structura, elementele obligatorii și regulile de validare sunt stabilite printr-un act tehnic distinct de Codul fiscal, numit RO_CIUS. Cine generează facturi electronice fără să respecte exact această specificație riscă respingerea la validare, cu toate consecințele de întârziere pe care le implică.

## Temeiul legal

```
::: ghid-temei
„Se aprobă Specificațiile tehnice și de utilizare a elementelor de bază ale facturii electronice - RO_CIUS - și regulile operaționale specifice aplicabile la nivel național, prevăzute [în anexă]."
— Ordinul ministrului finanțelor nr. 1.366/2021 pentru aprobarea Specificațiilor tehnice și de utilizare a elementelor de bază ale facturii electronice - RO_CIUS, art. 1 (sursă: anaf_surse/ordin_1366_2021.html)
:::
```

Ce trebuie reținut din acest act și din contextul lui legal:

- **RO_CIUS este specificația tehnică românească**, derivată din standardul european EN 16931, care stabilește elementele obligatorii ale unei facturi electronice valide (identificare emitent/beneficiar, linii de factură, cote de TVA, totaluri) și regulile suplimentare specifice României.
- Actul a fost emis **în baza OUG nr. 120/2021**, ordonanța care a instituit sistemul național RO e-Factura — deci temeiul „de fond" al obligativității facturii electronice e distinct de temeiul „tehnic" care descrie exact structura XML.
- O factură care respectă vizual cerințele legale (TVA corect, mențiuni obligatorii) poate fi totuși **respinsă tehnic** de sistemul RO e-Factura dacă fișierul XML nu respectă structura RO_CIUS — cele două verificări (de conținut fiscal și de format tehnic) sunt separate.
- Sistemul RO e-Factura validează automat fișierul primit contra acestei scheme; o factură care nu trece validarea nu este considerată transmisă.

## Ce se greșește în practică

- Se generează facturi într-un format XML generic sau adaptat după un alt standard european (UBL simplu, fără particularitățile RO_CIUS), care trece de validări generice dar e respins de sistemul ANAF.
- Se presupune că un PDF „arată" ca o factură corectă, deci XML-ul generat din el e implicit valid — validarea RO e-Factura se face exclusiv pe structura XML, nu pe reprezentarea vizuală.
- Se ignoră regulile operaționale specifice naționale (mențiuni suplimentare față de EN 16931), aplicând doar structura europeană generică.

## Ce face iConta.eu

La data acestui ghid, `core/efactura_send.py`, `core/efactura_trimitere.py` și `core/efactura_import.py` implementează generarea, trimiterea și importul facturilor electronice către/de la sistemul RO e-Factura, cu teste dedicate de validare a structurii (`core/test_efactura_send.py`, `core/test_a10_efactura_baza_linie.py`) — confirmat direct din cod. Structura XML generată e verificată prin rulările proprii ale proiectului împotriva regulilor sistemului ANAF, conform disciplinei de lucru care cere probă funcțională reală, nu doar verificare de sintaxă, la orice schimbare care afectează generarea declarațiilor/documentelor fiscale.

[iConta.eu](/)
