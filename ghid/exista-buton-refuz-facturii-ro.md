---
title: "Există buton de refuz al facturii în RO e-Factura?"
description: "De ce sistemul RO e-Factura nu are un mecanism de „returnare" a facturii primite, ci doar un mesaj de obiecții către emitent, conform OUG 120/2021."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Există buton de refuz al facturii în RO e-Factura?

Nu, sistemul național RO e-Factura nu are un buton de „refuz" care să anuleze sau să respingă o factură primită. Odată comunicată destinatarului, factura electronică rămâne definitivă în sistem — mecanismul disponibil pentru destinatar este unul de obiecție, nu de returnare.

## Temeiul legal

::: ghid-temei
„ART. 4 [...]
(8) Factura electronică comunicată destinatarului nu se poate returna în sistemul național privind factura electronică RO e-Factura.
(9) În situația unei facturi electronice asupra căreia destinatarul are obiecții, acesta înștiințează emitentul facturii electronice, inclusiv în sistemul național privind factura electronică RO e-Factura, prin înscrierea unui mesaj în acest sens.
(10) Corecția facturii electronice comunicată destinatarului în sistemul RO e-Factura se efectuează conform art. 330 din Legea nr. 227/2015 privind Codul fiscal, cu modificările și completările ulterioare. Factura electronică corectată se transmite în cadrul aceluiași sistem național privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (8)-(10) (sursă: anaf_surse/oug_120_2021.txt)
:::

Mecanismul real, așa cum rezultă din text:

- **Nu există returnare**: o factură electronică comunicată deja destinatarului rămâne în sistem — nu poate fi „respinsă" sau ștearsă de destinatar prin platforma RO e-Factura (alin. (8)).
- **Există un mesaj de obiecții**: dacă destinatarul consideră factura greșită (sumă, cantitate, date de identificare etc.), poate înscrie un mesaj de obiecție în sistem, care înștiințează emitentul (alin. (9)) — acesta e echivalentul cel mai apropiat al unui „refuz", dar nu produce efectul juridic al unei respingeri automate.
- **Corectarea se face de emitent**, prin emiterea unei facturi corective conform art. 330 din Codul fiscal, transmisă tot prin sistemul RO e-Factura (alin. (10)) — destinatarul nu poate corecta singur factura, doar poate semnala problema.

## Ce se greșește în practică

- Se caută în aplicația RO e-Factura un buton echivalent celui din alte sisteme europene de e-invoicing, care permit respingerea formală a unei facturi — sistemul românesc nu are acest mecanism, conform textului legii.
- Se presupune că trimiterea unui mesaj de obiecție anulează obligațiile contabile sau fiscale legate de factura respectivă — mesajul e doar o înștiințare, factura rămâne în evidența sistemului până la o eventuală corecție emisă de furnizor.
- Se ignoră faptul că problemele de fond (marfă neconformă, litigiu comercial) se rezolvă prin mecanismele de drept civil/comercial dintre părți, nu prin sistemul RO e-Factura, care e un canal de raportare fiscală, nu o platformă de arbitraj comercial.

## Ce face iConta.eu

iConta.eu se integrează cu sistemul RO e-Factura pentru transmiterea și primirea facturilor electronice. Aplicația nu poate oferi o funcție de „refuz" a unei facturi primite, pentru că un astfel de mecanism nu există la nivelul sistemului național — utilizatorul poate semnala eventualele obiecții direct emitentului, prin mesajul disponibil în sistem, conform procedurii de la art. 4 alin. (9) din OUG 120/2021.

[iConta.eu](/)
