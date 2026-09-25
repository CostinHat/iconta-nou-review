---
title: "Cum import automat facturile primite în contabilitate?"
description: "Ce prevede legea despre calitatea de document justificativ a facturii electronice și cum ajunge o factură primită prin RO e-Factura în evidența contabilă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum import automat facturile primite în contabilitate?

Factura electronică primită prin RO e-Factura nu este doar un fișier XML „descărcat" — legea îi recunoaște calitatea de document justificativ pentru înregistrarea în contabilitate, ceea ce face posibil (și de dorit) ca preluarea ei în evidența contabilă să fie automatizată.

## Temeiul legal

::: ghid-temei
„(6) Exemplarul original al facturii electronice se consideră fişierul de tip XML însoţit de semnătura electronică a Ministerului Finanţelor."
— OUG nr. 120/2021, art. 4 alin. (6) (sursă: anaf_surse/oug_120_2021.txt)
:::

Din acest text, coroborat cu restul articolului 4, rezultă statutul facturii electronice descărcate din sistem:

- Fișierul XML semnat electronic de Ministerul Finanțelor **este** originalul facturii — nu o copie sau o formă auxiliară a unui document „adevărat" emis altfel.
- Data comunicării către destinatar este data la care factura devine disponibilă pentru descărcare din sistem (art. 4 alin. (7)) — moment relevant pentru înregistrarea contabilă și pentru exercitarea dreptului de deducere a TVA.
- Odată comunicată, factura electronică nu se mai poate returna în sistem (art. 4 alin. (8)) — orice corecție se face printr-o factură de corecție nouă, transmisă tot prin RO e-Factura, conform art. 330 din Codul fiscal.

Legea nu obligă, însă, la o metodă anume de „import" în programul de contabilitate — stabilește doar valoarea juridică a documentului descărcat din sistem, lăsând mecanismul tehnic de preluare la latitudinea fiecărui software.

## Ce se greșește în practică

- Se introduc manual, din nou, datele unei facturi deja disponibile ca XML structurat în RO e-Factura, deși informația este deja acolo, în format prelucrabil automat.
- Se presupune că o factură descărcată din SPV este automat „înregistrată" în contabilitate doar prin faptul că a fost descărcată — descărcarea și înregistrarea contabilă sunt operațiuni distincte, a doua cerând validare și contare.
- Se contabilizează automat, fără verificare umană, facturi primite prin sistem — riscul este ca o factură cu date incorecte sau un furnizor greșit identificat să ajungă direct în evidență, fără control.

## Ce face iConta.eu

iConta.eu automatizează partea de **preluare**, nu și pe cea de validare finală. Un job programat (`core/spv_receive.py`) interoghează periodic contul SPV al firmei, descarcă facturile noi primite prin RO e-Factura și le inserează ca ciornă în `efactura_primite`, folosind parserul XML din `core/efactura_import.py` pentru a extrage furnizor, sumă, TVA și liniile facturii. Din acel moment, factura apare în aplicație ca ciornă, dar **nu devine automat o cheltuială înregistrată** — contabilul trebuie să o valideze explicit (principiul celor patru ochi), moment în care i se atribuie contul de cheltuială și intră efectiv în evidență. Deduplicarea (aceeași factură descărcată la mai multe rulări) este tratată la nivel de bază de date, pe identificatorul mesajului ANAF.

[iConta.eu](/)
