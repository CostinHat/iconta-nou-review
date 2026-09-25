---
title: "Cum import XML-ul e-Factura în programul de contabilitate?"
description: "Structura facturii electronice RO e-Factura, conform standardului european, și modul în care poate fi preluată automat într-un program de contabilitate."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum import XML-ul e-Factura în programul de contabilitate?

Factura electronică emisă prin RO e-Factura nu este un format liber — respectă o structură XML standardizată la nivel european, ceea ce face posibilă citirea și prelucrarea ei automată de către orice program pregătit pentru acest standard.

## Temeiul legal

::: ghid-temei
„(1) Structura facturii electronice respectă:
a) specificaţiile tehnice şi de utilizare a elementelor de bază ale facturii electronice aşa cum sunt prevăzute în standardul european SR EN 16931-1, care sunt aplicabile la nivel naţional;
b) specificaţiile tehnice şi de utilizare a elementelor de bază ale facturii electronice - RO_CIUS - şi regulile operaţionale specifice aplicabile la nivel naţional;
c) conţinutul semantic aşa cum este descris în standardul SR EN 16931-1, sintaxele identificate în CEN/TS 16931-2 [...] şi corelarea adecvată definită în subpartea aplicabilă a CEN/TS 16931-3."
— OUG nr. 120/2021, art. 4 alin. (1) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce înseamnă, practic, pentru importul într-un program de contabilitate:

- Orice factură validată de RO e-Factura respectă aceeași structură semantică (SR EN 16931-1) și aceleași reguli specifice naționale (RO_CIUS) — un parser scris pentru acest standard poate citi orice factură emisă prin sistem, indiferent de aplicația care a generat-o.
- Elementele principale ale facturii (art. 4 alin. (2)) — identificatori, date privind emitentul și destinatarul, liniile de facturare, defalcarea TVA, totalul — sunt cele care trebuie extrase pentru a reconstitui factura în evidența contabilă.
- Factura descărcată vine ca fișier XML însoțit de semnătura electronică a Ministerului Finanțelor (art. 4 alin. (6)), iar acest ansamblu este exemplarul original — importul trebuie să pornească de la acest fișier, nu de la o conversie ulterioară (PDF, imprimare) care ar putea pierde informație structurată.

## Ce se greșește în practică

- Se încearcă citirea facturii doar din reprezentarea vizuală (PDF-ul generat pentru afișare), pierzând astfel câmpuri structurate care există în XML dar nu apar clar în forma tipărită.
- Se presupune că toate facturile electronice au aceeași denumire de câmpuri ca alte formate de factură electronică folosite anterior în alte țări — RO_CIUS are particularități naționale peste standardul european de bază.
- Se ignoră faptul că o factură de corecție (art. 4 alin. (10), conform art. 330 Cod fiscal) este tot un fișier XML nou, transmis prin același sistem — trebuie tratată ca atare la import, nu ca o simplă notă atașată facturii inițiale.

## Ce face iConta.eu

iConta.eu are un parser dedicat pentru structura RO e-Factura: `core/efactura_import.py` citește arhiva ZIP descărcată din SPV, identifică fișierul XML (format UBL 2.1 / CIUS-RO) și extrage numărul facturii, data emiterii, scadența, datele furnizorului și clientului (după CUI), totalul cu TVA, valoarea TVA, moneda și liniile facturii. Direcția facturii (emisă sau primită) se determină automat prin compararea CUI-ului furnizorului din XML cu CUI-ul firmei din aplicație. Rezultatul parsării alimentează fluxul descris în ghidul despre importul automat al facturilor primite, unde validarea finală rămâne, totuși, la latitudinea contabilului.

[iConta.eu](/)
