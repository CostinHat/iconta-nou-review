---
title: "De ce expiră tokenul pentru e-Factura"
description: "Ce prevede legea despre transmiterea prin mijloace electronice a facturilor către ANAF și de ce autentificarea în Spațiul Privat Virtual are o durată limitată."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# De ce expiră tokenul pentru e-Factura

Firmele care transmit facturi prin RO e-Factura se lovesc, la un moment dat, de reconectare: tokenul de acces expiră și cabinetul contabil sau firma trebuie să se autentifice din nou. Merită separat ce spune legea despre obligația de a folosi acest canal electronic de ceea ce e, de fapt, o decizie tehnică a ANAF.

## Temeiul legal

::: ghid-temei
„(1) Ministerul Finanțelor, prin Centrul Național pentru Informații Financiare, creează, dezvoltă și administrează sistemul național privind factura electronică RO e-Factura.
(2) Sistemul național privind factura electronică RO e-Factura reprezintă ansamblul de principii, reguli și aplicații informatice având drept scop primirea facturii electronice de la emitent [...], stocarea prin mijloace electronice a facturilor și transmiterea către destinatar."
— OUG nr. 120/2021, art. 3 alin. (1)-(2) (sursă: anaf_surse/oug_120_2021.txt)
:::

**Limitare declarată:** legea de mai sus stabilește *obligația* de a folosi sistemul RO e-Factura și cadrul lui general, dar **durata de valabilitate a tokenului OAuth folosit la autentificarea în Spațiul Privat Virtual (SPV) nu e stabilită printr-un act normativ publicat în Monitorul Oficial** — e o decizie tehnică de implementare a ANAF, documentată doar în specificațiile tehnice ale platformei, nu într-o lege sau ordin. Nu am găsit, în sursele verificate, un temei legal care să fixeze acest termen; redirecționăm onest către cadrul legal cel mai apropiat — obligația de utilizare a sistemului (OUG 120/2021) și dreptul contribuabilului de a transmite cereri prin mijloace electronice de transmitere la distanță, inclusiv prin SPV, prevăzut la art. 79 din Codul de procedură fiscală (Legea nr. 207/2015).

Practic, ce se știe cu certitudine este:

- Autentificarea în SPV/e-Factura se face prin certificat digital calificat, iar sesiunea rezultată (tokenul de acces) are o durată limitată, după care reautentificarea e obligatorie.
- Fără reînnoire, transmiterea facturilor se oprește tăcut — riscul nu e o eroare vizibilă, ci o firmă „deconectată" fără să știe.
- Obligația de fond (transmiterea facturilor prin sistemul național) rămâne valabilă indiferent de detaliile tehnice ale autentificării.

## Ce se greșește în practică

- Se așteaptă ca expirarea tokenului să genereze o notificare vizibilă din partea ANAF — de multe ori eșecul e tăcut, iar facturile pur și simplu nu mai ajung.
- Se reface autentificarea manual abia după ce apar erori de transmitere, deși reînnoirea se poate face din timp, înainte de expirare.
- Se confundă expirarea tokenului tehnic cu o problemă legală sau cu o modificare a obligației de facturare electronică — sunt lucruri complet separate.

## Ce face iConta.eu

iConta.eu automatizează reîmprospătarea tokenului SPV: un proces zilnic (`core/spv_refresh.py`) identifică toate token-urile ale căror acces expiră în curând (cu o marjă de siguranță configurabilă) și le reînnoiește automat, fără intervenție manuală. Eșecul reîmprospătării unui token nu blochează celelalte conexiuni active, iar dacă reînnoirea nu reușește, aplicația semnalează firma afectată — astfel încât deconectarea de la SPV să nu treacă neobservată.

[iConta.eu](/)
