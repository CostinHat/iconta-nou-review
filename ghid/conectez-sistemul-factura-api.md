---
title: "Cum conectez sistemul meu la e-Factura prin API"
description: "Interoperabilitatea RO e-Factura cu aplicațiile terțe este prevăzută explicit de lege, iar conectarea se face prin autorizare OAuth2, pornind de la certificatul digital calificat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum conectez sistemul meu la e-Factura prin API

Nu e nevoie de o soluție ocolitoare pentru a conecta propriul sistem la RO e-Factura — legea prevede explicit că sistemul trebuie să fie interoperabil cu aplicațiile de facturare ale operatorilor economici, iar conectarea se face printr-o autorizare bazată pe certificatul digital al firmei.

## Temeiul legal

::: ghid-temei
„Sistemul naţional privind factura electronică RO e-Factura asigură interoperabilitatea cu sistemele de facturare ale operatorilor economici."
— OUG nr. 120/2021, art. 16 (sursă: anaf_surse/oug_120_2021.txt)
:::

Coroborat cu regulile de identificare electronică, conectarea unui sistem propriu presupune:

- **Autorizarea prealabilă** cu certificatul digital calificat al firmei sau PFA-ului (art. 80 alin. (1) lit. a) din Codul de procedură fiscală) — fără această autorizare, nicio aplicație terță nu poate acționa în numele contribuabilului.
- **Respectarea structurii facturii** (SR EN 16931-1, RO_CIUS) pentru orice document transmis prin API — interoperabilitatea nu înseamnă un format liber, ci conformarea la același standard folosit și de interfața web a ANAF.
- Procedura tehnică exactă de conectare (protocol de autorizare, formatul apelurilor) este stabilită de Ministerul Finanțelor/ANAF prin acte tehnice, conform art. 3 alin. (4) din aceeași ordonanță — legea de bază lasă implementarea concretă la nivel de procedură ANAF, nefixată direct în text.

## Ce se greșește în practică

- Se presupune că orice aplicație poate trimite facturi „automat" fără nicio autorizare a titularului contului fiscal — accesul este întotdeauna condiționat de autorizarea explicită, cu certificat calificat, a persoanei/firmei respective.
- Se confundă conectarea API cu accesul manual la portalul SPV — sunt canale tehnice diferite, dar amândouă necesită aceeași bază de autentificare (certificatul calificat).
- Se ignoră faptul că o factură trimisă prin API care nu respectă structura standard este respinsă la fel ca una încărcată manual greșit — API-ul nu relaxează cerințele de conformitate ale facturii.

## Ce face iConta.eu

iConta.eu este ea însăși un exemplu de „sistem propriu" conectat prin API la RO e-Factura: modulul `core/spv_conector.py` implementează autorizarea OAuth2 cu ANAF, iar `core/efactura_send.py` folosește acest acces pentru a genera și transmite facturile în format CIUS-RO. Firma sau PFA-ul autorizează o singură dată conexiunea, folosind certificatul digital calificat; ulterior, aplicația reînnoiește automat accesul tehnic (refresh token), fără intervenție repetată.

[iConta.eu](/)
