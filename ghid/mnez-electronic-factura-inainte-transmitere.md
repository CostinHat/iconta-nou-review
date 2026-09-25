---
title: "Cum semnez electronic factura înainte de transmitere"
description: "Semnătura electronică pe factura din RO e-Factura este aplicată de Ministerul Finanțelor la acceptare, nu de emitent înainte de transmitere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum semnez electronic factura înainte de transmitere

Răspunsul scurt: nu tu semnezi factura înainte de a o transmite. În RO e-Factura, semnătura electronică este aplicată de sistem, după ce factura trece validarea de structură — nu de emitent, înainte de trimitere.

## Temeiul legal

::: ghid-temei
„(4) În situaţia în care factura electronică transmisă respectă structura prevăzută la alin. (1), se aplică semnătura electronică a Ministerului Finanţelor şi se comunică de îndată destinatarului. Aplicarea semnăturii electronice a Ministerului Finanţelor atestă primirea acesteia în sistemul naţional privind factura electronică RO e-Factura."
— OUG nr. 120/2021, art. 4 alin. (4) (sursă: anaf_surse/oug_120_2021.txt)
:::

Mecanismul descris de lege este simplu, dar diferit de intuiția „semnez, apoi trimit":

- Emitentul transmite factura electronică (fișierul XML) **fără să aplice el o semnătură** pe ea în prealabil — condiția este ca structura facturii să respecte specificațiile tehnice (SR EN 16931-1, RO_CIUS).
- **Sistemul RO e-Factura**, prin Ministerul Finanțelor, aplică semnătura electronică după validare — acest moment atestă primirea facturii în sistem, nu inițiativa emitentului.
- Dacă structura nu este respectată, emitentul primește un mesaj cu erorile identificate (art. 4 alin. (5)) și trebuie să corecteze și să retransmită — abia forma corectă, odată acceptată, primește semnătura.
- Exemplarul original al facturii este definit ca fișierul XML însoțit de semnătura Ministerului Finanțelor (art. 4 alin. (6)) — semnătura face parte din ce definește „originalul", nu este un pas pregătitor înaintea transmiterii.

## Ce se greșește în practică

- Se caută o funcție de „semnare" a facturii înainte de a o încărca în sistem, presupunând că e nevoie de o semnătură digitală proprie a emitentului — nu este cerută pentru validitatea facturii în RO e-Factura.
- Se confundă semnătura electronică a Ministerului Finanțelor cu semnătura pe alte documente fiscale (de exemplu, declarații depuse cu certificat propriu) — pentru factura RO e-Factura, semnătura care contează este cea aplicată de sistem la acceptare.
- Se amână transmiterea facturii în așteptarea unei semnături care ar trebui, credem, obținută separat — de fapt, transmiterea este pasul care declanșează, dacă factura e corectă, aplicarea automată a semnăturii.

## Ce face iConta.eu

iConta.eu transmite factura prin RO e-Factura fără să ceară vreo semnătură suplimentară din partea utilizatorului — generarea XML-ului (`core/efactura_send.py`) și transmiterea către ANAF se fac direct, iar validarea de structură și aplicarea semnăturii electronice a Ministerului Finanțelor rămân, așa cum prevede legea, în sarcina sistemului ANAF. Starea trimiterii (acceptată/respinsă, cu semnătura aplicată) este urmărită automat de `core/spv_poll.py`, iar în caz de respingere, aplicația indică erorile primite de la ANAF pentru corectare.

[iConta.eu](/)
