---
title: e-Factura pentru avansuri încasate?
description: Legislația RO e-Factura (OUG 120/2021) nu conține nicio prevedere distinctă pentru facturile de avans; ele intră sub regimul general de factură electronică, iar codul UBL exact folosit de iConta.eu pentru tipul de factură nu a putut fi confirmat contra specificației tehnice RO_CIUS.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# e-Factura pentru avansuri încasate?

Facturile de avans emise către clienți intră, la fel ca orice altă factură, sub obligația RO e-Factura. Întrebarea care apare des este dacă există un tratament tehnic special — un cod de tip de factură distinct — pentru facturile de avans în profilul românesc.

## Temeiul legal

::: ghid-temei
"a) factură electronică - factura emisă, transmisă şi primită într-un format electronic structurat de tip XML, care permite prelucrarea sa electronică şi automată;"

"(2) Prin excepție de la prevederile alin. (1), exigibilitatea taxei intervine: ... b) la data la care se încasează avansul, pentru plățile în avans efectuate înainte de data la care intervine faptul generator. Avansurile reprezintă plata parțială sau integrală a contravalorii bunurilor și serviciilor, efectuată înainte de data livrării ori prestării acestora;"
:::

## Ce spune (și ce nu spune) legislația

OUG 120/2021 definește factura electronică în termeni generali, ca document XML structurat, fără să distingă tipuri de facturi. Secțiunea care reglementează domeniul B2B (art. 10 și următoarele) nu menționează nicăieri explicit facturile de avans ca o categorie separată — o căutare directă a termenului "avans" în text nu găsește niciun rezultat.

Standardul tehnic UBL/EN16931, pe care se bazează factura electronică europeană, prevede totuși un cod de tip de document distinct pentru avansuri: `386` ("Prepayment invoice"), diferit de codul standard `380` ("Commercial invoice") folosit pentru facturile obișnuite. Dacă profilul tehnic românesc (RO_CIUS) impune sau nu folosirea codului `386` pentru facturile de avans nu poate fi confirmat fără specificația tehnică RO_CIUS publicată de ANAF/Ministerul Finanțelor — document care nu a fost verificat la sursă pentru acest ghid.

## Ce se greșește în practică

- Se presupune, fără verificare, că orice factură de avans trebuie neapărat să poarte codul UBL `386`, deși acest lucru nu e confirmat pentru profilul românesc.
- Se ignoră complet distincția UBL dintre `380` și `386`, fără să se verifice dacă sistemul folosit generează consecvent același cod indiferent de tipul facturii.
- Se amână trimiterea facturii de avans în RO e-Factura, considerând-o eronat "opțională" sau "informală" — legea nu face nicio distincție de acest fel: factura de avans e o factură electronică obișnuită, supusă acelorași termene.
- Se confundă obligația de emitere e-Factura cu momentul exigibilității TVA — sunt două obligații distincte, care nu se condiționează reciproc.

## Ce face iConta.eu

Modulul de trimitere e-Factura (`core/efactura_send.py`, linia 211) generează necondiționat `<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>` pentru orice factură trimisă — inclusiv pentru facturile de avans emise prin `nota_avans_incasat`. Nu există în cod nicio ramificație care să seteze codul `386` pentru facturile de avans.

Onest spus: nu putem confirma, pe baza surselor legale disponibile, dacă acest lucru reprezintă o eroare sau este o practică acceptabilă în profilul RO_CIUS — documentul tehnic care ar clarifica exact acest punct nu a fost identificat în sursele verificate. Dacă lucrați cu volume mari de facturi de avans transmise prin RO e-Factura, recomandăm verificarea explicită a specificației RO_CIUS curente la ANAF/Ministerul Finanțelor înainte de a considera codul `380` corect sau greșit pentru acest tip de document.

[iConta.eu](/)
