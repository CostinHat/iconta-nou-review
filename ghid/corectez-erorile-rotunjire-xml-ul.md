---
title: "Cum corectez erorile de rotunjire din XML-ul e-Factura?"
description: "De ce apar diferențe de rotunjire în fișierul XML al facturii electronice și care este mecanismul legal de corectare a unei facturi deja transmise prin RO e-Factura."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez erorile de rotunjire din XML-ul e-Factura?

Facturile cu multe linii, cote de TVA diferite sau discounturi pe linie produc uneori mici diferențe de rotunjire între totalul calculat linie cu linie și totalul de pe factură. În formatul UBL cerut de RO e-Factura, aceste diferențe pot fi respinse de validator sau semnalate ca eroare — iar odată transmisă, o factură electronică nu poate fi retrasă din sistem, doar corectată.

## Temeiul legal

::: ghid-temei
„(8) Factura electronică comunicată destinatarului nu se poate returna în sistemul naţional privind factura electronică RO e-Factura. (9) În situaţia unei facturi electronice asupra căreia destinatarul are obiecţii, acesta înştiinţează emitentul facturii electronice [...]. (10) Corecţia facturii electronice comunicată destinatarului în sistemul RO e-Factura se efectuează conform art. 330 din Legea nr. 227/2015 privind Codul fiscal [...]. Factura electronică corectată se transmite în cadrul aceluiaşi sistem naţional privind factura electronică RO e-Factura."
— OUG nr. 120/2021, art. 4 alin. (8)-(10) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce înseamnă asta practic pentru o eroare de rotunjire:

- Nu există în legea română o regulă fiscală specifică pentru „erorile de rotunjire" din XML — cerințele de rotunjire (de exemplu, precizia zecimalelor pe fiecare linie și pe total) vin din **standardul european EN 16931**, aplicabil facturii electronice prin specificațiile tehnice RO_CIUS, nu dintr-un articol distinct din Codul fiscal.
- O dată transmisă și comunicată destinatarului, factura electronică **nu poate fi ștearsă sau retrasă** din sistemul RO e-Factura (art. 4 alin. (8)) — inclusiv atunci când eroarea e doar o diferență de câțiva bani rezultată din rotunjire.
- Corectarea unei astfel de erori urmează **mecanismul general** de corectare a facturilor, prevăzut la art. 330 din Codul fiscal: fie se emite o factură de stornare (cu valorile cu minus) urmată de una corectă, fie o singură factură care conține atât corecția, cât și valorile corecte — niciodată o „editare" a facturii deja transmise.
- Factura de corecție se transmite, la rândul ei, prin același sistem RO e-Factura (art. 4 alin. (10)) — corectarea unei erori de rotunjire nu iese din fluxul obligatoriu al facturării electronice.

## Ce se greșește în practică

- Se încearcă retransmiterea facturii inițiale cu suma corectată, sub același număr — sistemul RO e-Factura nu permite suprascrierea unei facturi deja comunicate; trebuie urmată procedura de corecție cu factură nouă.
- Se ignoră diferența de rotunjire până la validare, iar respingerea de la validator e tratată ca „bug tehnic", când de fapt reflectă o regulă de precizie a totalurilor impusă de standardul EN 16931.
- Se emite factura de corecție fără mențiunea cerută de art. 330 alin. (1) lit. b) (referința la numărul și data facturii corectate), ceea ce face dificilă trasabilitatea la un control ulterior.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează și transmite facturi către sistemul RO e-Factura prin motorul propriu (`core/efactura_trimitere.py`, `core/efactura_send.py`), dar corectarea unei facturi deja transmise, inclusiv pentru diferențe de rotunjire, urmează fluxul standard de emitere a unei facturi de corecție/stornare — nu există în aplicație un mecanism de „editare" a unei facturi deja comunicate prin sistem.

[iConta.eu](/)
