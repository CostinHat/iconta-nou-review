---
title: "Cum funcționează integrarea API cu RO e-Factura?"
description: "Ce prevede OUG 120/2021 despre interoperabilitatea sistemului RO e-Factura cu aplicațiile de facturare ale operatorilor economici."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum funcționează integrarea API cu RO e-Factura?

RO e-Factura nu este gândit ca un portal în care se încarcă manual facturi, una câte una — legea prevede explicit că sistemul trebuie să fie interoperabil cu aplicațiile de facturare ale firmelor, adică accesibil prin API.

## Temeiul legal

::: ghid-temei
„Sistemul naţional privind factura electronică RO e-Factura asigură interoperabilitatea cu sistemele de facturare ale operatorilor economici."
— OUG nr. 120/2021, art. 16 (sursă: anaf_surse/oug_120_2021.txt)
:::

Din text și din articolele conexe rezultă cadrul general al integrării:

- Sistemul este administrat de Ministerul Finanțelor, prin Centrul Național pentru Informații Financiare, care „creează, dezvoltă şi administrează" RO e-Factura (art. 3 alin. (1)).
- Procedura tehnică de utilizare și funcționare a sistemului se stabilește prin ordin al ministrului finanțelor (art. 3 alin. (4)) — detaliile de implementare API (formate, endpoint-uri, autentificare) nu sunt fixate direct în ordonanță, ci în acte tehnice ulterioare ale ANAF.
- Factura electronică transmisă prin API trebuie să respecte aceeași structură XML (SR EN 16931-1 / RO_CIUS) ca și cea încărcată manual — integrarea prin API nu schimbă cerințele de conținut ale facturii, doar canalul de transmitere.

## Ce se greșește în practică

- Se presupune că o aplicație terță poate trimite facturi „în numele" unei firme fără nicio autorizare prealabilă — accesul API este condiționat de autorizarea explicită a contribuabilului (prin certificat calificat, conform art. 80 din Codul de procedură fiscală) pentru aplicația respectivă.
- Se confundă integrarea API cu depunerea declarațiilor fiscale obișnuite — RO e-Factura are propriul flux (transmitere, validare structurală, semnătură electronică a Ministerului Finanțelor, notificare destinatar), diferit de cel al unei declarații informative.
- Se ignoră faptul că factura respinsă la validarea structurală trebuie corectată și retransmisă în același sistem (art. 4 alin. (5)) — o eroare de format nu se remediază „pe cont propriu", ci tot prin API/portal.

## Ce face iConta.eu

iConta.eu are o integrare API reală cu RO e-Factura, nu doar o interfață de încărcare manuală. Modulul `core/efactura_send.py` generează XML-ul UBL 2.1 / CIUS-RO din facturile emise în aplicație și îl transmite prin apeluri directe la ANAF (endpoint-urile `api.anaf.ro/.../FCTEL/rest`), folosind conectorul OAuth2 din `core/spv_conector.py`. Primirea funcționează simetric: un job programat (`core/spv_poll.py`) interoghează periodic starea trimiterilor, iar `core/spv_receive.py` descarcă automat facturile primite de la furnizori și le pregătește ca ciornă pentru validare de către contabil, fără să creeze automat o cheltuială — verificarea rămâne manuală, pe principiul celor patru ochi.

[iConta.eu](/)
