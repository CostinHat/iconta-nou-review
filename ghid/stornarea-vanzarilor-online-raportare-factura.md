---
title: "Stornarea vânzărilor online: raportare în e-Factura"
description: "Regula de corectare a unei facturi electronice deja comunicate destinatarului în sistemul RO e-Factura, potrivit OUG nr. 120/2021 și Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Stornarea vânzărilor online: raportare în e-Factura

Odată ce o factură electronică a fost comunicată destinatarului prin sistemul RO e-Factura, ea nu mai poate fi „ștearsă” sau retrasă — orice corecție (inclusiv stornarea unei vânzări online, de exemplu în caz de retur) se face printr-un document distinct, transmis tot prin sistemul național.

## Temeiul legal

::: ghid-temei
„Factura electronică comunicată destinatarului nu se poate returna în sistemul naţional privind factura electronică RO e-Factura. [...] Corecţia facturii electronice comunicată destinatarului în sistemul RO e-Factura se efectuează conform art. 330 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare. Factura electronică corectată se transmite în cadrul aceluiaşi sistem naţional privind factura electronică RO e-Factura."
— OUG nr. 120/2021, art. 4 alin. (8) și (10) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce presupune, practic, stornarea unei vânzări online deja facturate prin e-Factura:

- Factura inițială **rămâne** în sistemul RO e-Factura, ca document original — nu se poate retrage sau elimina.
- Corectarea (inclusiv stornarea, integrală sau parțială, a unei vânzări) se face conform **art. 330 Cod fiscal** (regulile de facturare, respectiv emiterea unei facturi de corecție/stornare care face trimitere la factura inițială), iar noul document se **transmite din nou** prin sistemul RO e-Factura.
- Dacă factura vizată de corecție a fost respinsă de client în sistem (obiecțiuni, art. 4 alin. (9)), procesul de stornare urmează aceeași logică: emitentul corectează și retransmite documentul prin sistem, nu îl modifică „pe loc”.
- Pentru vânzările online B2C, unde nu se aplică obligația B2B de transmitere prin e-Factura decât dacă firma a optat pentru sistem, regula de corecție a facturii inițiale rămâne, în esență, aceeași (emiterea unui document de stornare distinct).

## Ce se greșește în practică

- Se încearcă „anularea” facturii direct în sistemul de facturare al firmei, fără emiterea și transmiterea unui document de corecție prin RO e-Factura, lăsând factura inițială, nemodificată, ca document valabil în sistemul ANAF.
- Se emite factura de stornare, dar nu se retransmite prin sistemul național, considerând că e suficientă corectarea în evidența internă a firmei.
- Se confundă stornarea (document de corecție distinct, cu trimitere la factura inițială) cu o presupusă posibilitate de „ștergere” a facturii deja comunicate — sistemul nu permite retragerea documentelor comunicate.

## Ce face iConta.eu

iConta.eu emite facturi și le transmite prin sistemul RO e-Factura, iar stornarea unei vânzări (integrală sau parțială) se face prin emiterea unui document de corecție din aplicație, care se transmite, la rândul lui, prin același sistem. Urmărirea confirmării stornării în SPV rămâne la latitudinea utilizatorului.

[iConta.eu](/)
