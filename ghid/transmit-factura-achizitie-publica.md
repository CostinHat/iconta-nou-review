---
title: "Cum transmit o factură pentru o achiziție publică"
description: "Regimul RO e-Factura pentru relația B2G, aplicabil atunci când un operator economic optează pentru facturarea electronică într-un contract de achiziție publică."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum transmit o factură pentru o achiziție publică

Facturarea către o instituție publică, în cadrul unui contract de achiziție publică (relație B2G — business to government), are un regim distinct de facturarea electronică obligatorie pentru relațiile dintre operatori economici (B2B). Cadrul specific este stabilit de OUG nr. 120/2021, care reglementează sistemul național RO e-Factura.

## Temeiul legal

::: ghid-temei
„ART. 5 Facturarea electronică în domeniul achiziţiilor publice se aplică în cazul existenţei unei relaţii B2G, definită conform art. 2 alin. (1) lit. m), în situaţia în care operatorii economici optează pentru utilizarea sistemului naţional privind factura electronică RO e-Factura."
— OUG nr. 120/2021 privind sistemul național RO e-Factura, art. 5, Secțiunea a 3-a — Facturarea electronică în domeniul achizițiilor publice (sursă: anaf_surse/oug_120_2021.txt)
:::

- Pentru relația B2G, transmiterea facturii prin RO e-Factura se face atunci când operatorul economic **optează** pentru acest sistem — textul legii leagă aplicarea explicit de opțiunea operatorului economic, în contextul unei relații B2G.
- Odată ce operatorul economic a optat pentru RO e-Factura într-o relație B2G, potrivit art. 7 alin. (1), acesta are obligația de **a emite doar facturi electronice** și de a folosi acest sistem pentru transmiterea lor către toți destinatarii vizați.
- Există excepții explicite (art. 6): facturile emise ca urmare a executării unor contracte clasificate potrivit legii, sau a unor contracte de achiziție publică pentru care s-au impus măsuri speciale de securitate pentru protejarea unor interese esențiale ale statului, nu intră sub incidența acestui regim.
- Dacă destinatarul (instituția/entitatea contractantă) are obiecții asupra unei facturi electronice transmise, acesta înștiințează emitentul, inclusiv prin înscrierea unui mesaj în sistemul RO e-Factura; corecția facturii se efectuează conform art. 330 din Codul fiscal și se transmite tot prin sistemul național.

## Ce se greșește în practică

- Se presupune că facturarea în achiziții publice funcționează după exact aceleași reguli ca facturarea electronică obligatorie B2B, ignorând reglementarea specifică B2G de la art. 5-7 din OUG 120/2021.
- Se transmit facturi în afara sistemului RO e-Factura după ce operatorul economic a optat deja pentru acesta într-o relație B2G, deși legea impune atunci exclusivitatea sistemului național.
- Se încearcă returnarea unei facturi electronice deja comunicate destinatarului prin sistem — legea interzice explicit acest lucru; corecțiile se fac printr-o factură corectată, nu prin anularea celei transmise.
- Nu se verifică dacă respectivul contract de achiziție publică se încadrează la excepțiile de la art. 6 (contracte clasificate sau cu măsuri speciale de securitate), care scot factura de sub incidența acestui regim.

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu are un motor de generare și transmitere a facturilor electronice conform standardului RO e-Factura (`core/efactura_send.py` — generator XML UBL 2.1/CIUS-RO — și `core/efactura_trimitere.py` — orchestrarea trimiterii către ANAF). Modulul acoperă fluxul general de trimitere e-Factura (generare XML, upload prin API-ul ANAF, verificare stare); nu am găsit însă, în cod, o logică dedicată specific relației B2G din achizițiile publice (de exemplu, marcarea distinctă a unei facturi ca fiind emisă în cadrul unui contract de achiziție publică) — pentru contribuabilul care optează pentru RO e-Factura într-o astfel de relație, mecanismul tehnic de trimitere folosit este cel general de e-Factura din aplicație.

[iConta.eu](/)
