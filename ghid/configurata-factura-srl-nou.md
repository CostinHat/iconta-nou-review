---
title: "Când trebuie configurată e-Factura pentru un SRL nou"
description: "De la ce moment îi revine unui SRL nou-înființat obligația de transmitere a facturilor în sistemul RO e-Factura și în ce termen."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când trebuie configurată e-Factura pentru un SRL nou

Legea nu prevede o perioadă de grație legată de vechimea firmei pentru obligația RO e-Factura — un SRL nou-înființat intră sub incidența ei din momentul în care emite prima factură către un alt operator economic stabilit în România, în relație B2B. Nu există un termen de "așteptare" de câteva luni de la înființare.

## Temeiul legal

::: ghid-temei
„Furnizorii prevăzuți la alin. (1)-(3) sunt obligați să transmită facturile emise către destinatari conform prevederilor art. 319 din Legea nr. 227/2015, cu modificările și completările ulterioare, cu excepția situației în care atât furnizorul/prestatorul, cât și destinatarul sunt înregistrați în Registrul RO e-Factura.
(6) Termenul-limită pentru transmiterea facturilor prevăzute la alin. (1)-(3) în sistemul național privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită prevăzută pentru emiterea facturii la art. 319 alin. (16) din Legea nr. 227/2015, cu modificările și completările ulterioare."
— Legea nr. 296/2023, art. LIX alin. (5) și (6) (sursă: anaf_surse/legea_296_2023_masuri_fiscal_bugetare_asigurarea_sustenabilitatii.txt)
:::

- **Obligația se leagă de calitatea de "persoană impozabilă stabilită în România"**, dobândită de la înființare, nu de o vechime minimă a firmei — deci un SRL nou trebuie să fie pregătit din prima factură emisă în relație B2B.
- **Termenul de transmitere e de 5 zile lucrătoare de la emitere**, indiferent de vechimea firmei, iar nerespectarea lui atrage amenda prevăzută la art. LIX alin. (7).
- **Configurarea practică** (certificat digital, acces SPV, generarea facturii electronice) trebuie deci pregătită înainte de emiterea primei facturi către un alt operator economic, nu tratată ca pas ulterior, "de rutină de rodaj".

## Ce se greșește în practică

- Se amână configurarea RO e-Factura pentru primele luni de activitate, considerând că firma nouă are o perioadă de grație — legea nu prevede așa ceva pentru firme noi ca atare.
- Se confundă termenul de transmitere în RO e-Factura (5 zile lucrătoare de la emitere) cu termenul de emitere a facturii (care rămâne cel din art. 319 alin. (16) Codul fiscal) — sunt două termene distincte care curg din momente diferite.
- Se presupune că obligația se activează abia la prima cerere din partea unui client — de fapt obligația legală există din start, indiferent dacă a fost sau nu respectată anterior.

## Ce face iConta.eu

Modulul de facturare al iConta.eu poate transmite facturile emise în sistemul RO e-Factura de la prima factură emisă de firmă, dacă utilizatorul a configurat conexiunea SPV/ANAF în profilul firmei — configurarea acestei conexiuni (certificat digital, autorizare OAuth) rămâne un pas manual, pe care aplicația nu îl activează automat la înființarea firmei în sistem.

[iConta.eu](/)
