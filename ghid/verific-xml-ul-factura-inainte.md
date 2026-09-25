---
title: "Cum verific XML-ul e-Factura înainte de transmitere?"
description: "Cum se verifică structura unui fișier XML de factură electronică față de standardul RO_CIUS înainte de a-l transmite prin sistemul RO e-Factura."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific XML-ul e-Factura înainte de transmitere?

Factura electronică din sistemul RO e-Factura nu e un simplu PDF, ci un fișier XML structurat care trebuie să respecte standardul european SR EN 16931-1 și specificațiile naționale RO_CIUS. Dacă structura nu e corectă, sistemul o respinge — de aceea, verificarea XML-ului înainte de transmitere economisește timp și evită erori care ajung să fie descoperite abia după respingerea facturii.

## Temeiul legal

::: ghid-temei
„Structura facturii electronice respectă: a) specificațiile tehnice și de utilizare a elementelor de bază ale facturii electronice așa cum sunt prevăzute în standardul european SR EN 16931-1 [...]; b) specificațiile tehnice și de utilizare a elementelor de bază ale facturii electronice - RO_CIUS - și regulile operaționale specifice aplicabile la nivel național [...].
(5) În situația în care factura electronică transmisă nu respectă structura prevăzută la alin. (1), emitentul primește mesaj cu erorile identificate. După corectarea erorilor identificate, factura electronică se transmite în cadrul aceluiași sistem național privind factura electronică RO e-Factura."
— OUG nr. 120/2021, art. 4 alin. (1), (5) (sursă: anaf_surse/oug_120_2021.txt)
:::

- Factura electronică e definită de lege ca „factura emisă, transmisă şi primită într-un format electronic structurat de tip XML, care permite prelucrarea sa electronică şi automată" (art. 2 alin. (1) lit. a)).
- Structura trebuie să respecte cumulativ: standardul european SR EN 16931-1, specificațiile naționale RO_CIUS și corelarea din CEN/TS 16931-3 (art. 4 alin. (1)).
- Dacă XML-ul respectă structura, Ministerul Finanțelor aplică semnătura electronică și factura e comunicată destinatarului „de îndată" (art. 4 alin. (4)).
- Dacă XML-ul nu respectă structura, emitentul primește un mesaj cu erorile identificate și trebuie să corecteze fișierul înainte de a-l retransmite (art. 4 alin. (5)).
- Exemplarul original al facturii electronice este „fișierul de tip XML însoțit de semnătura electronică a Ministerului Finanțelor" (art. 4 alin. (6)) — nu un export PDF ulterior.

## Ce se greșește în practică

- Se trimite XML-ul direct în sistemul RO e-Factura fără nicio verificare prealabilă, aflând abia din mesajul de eroare al ANAF ce e greșit.
- Se confundă validarea de structură (schematron CIUS-RO) cu validarea de conținut economic — un XML „valid" structural poate conține totuși date greșite (cotă TVA incorectă, CIF eronat).
- Se ignoră erorile de adresă (câmpurile CityName aferente vânzătorului/cumpărătorului), o cauză frecventă de respingere.
- Se presupune că PDF-ul generat de un soft de facturare este „factura", deși din punct de vedere legal doar fișierul XML semnat electronic de Ministerul Finanțelor are această calitate.

## Ce face iConta.eu

iConta.eu **generează XML-ul de factură (UBL, conform schemei curente) și îl trimite spre verificare la validatorul public oficial al ANAF** înainte de emitere — funcția `valideaza` din modulul `core/efactura_send.py` apelează adresa `https://webservicesp.anaf.ro/prod/FCTEL/rest/validare/{standard}`, validatorul de structură (schematron CIUS-RO) pus la dispoziție public de ANAF, fără a necesita token sau drept pe CIF. Astfel, XML-ul e verificat structural la sursă, înainte de a fi transmis efectiv prin sistemul RO e-Factura, reducând riscul de respingere ulterioară.

[iConta.eu](/)
