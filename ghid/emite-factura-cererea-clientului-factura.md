---
title: "Cum se emite factura la cererea clientului prin e-Factura"
description: Un bon fiscal emis unui client neidentificat nu naște obligație de e-Factura — dar în momentul în care clientul cere factură, documentul intră în sistem ca oricare altul, prin fluxul normal de generare și trimitere.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se emite factura la cererea clientului prin e-Factura

Vânzarea cu amănuntul are o regulă simplă, dar cu o schimbare de regim exact în momentul cererii de factură — merită înțeleasă clar, ca să nu rămână o factură netransmisă din neatenție.

## Temeiul legal

::: ghid-temei
„Exemplarul original al facturii electronice se consideră fişierul de tip XML însoţit de semnătura electronică a Ministerului Finanţelor." — OUG nr. 120/2021, art. 4 alin. (6).
:::

## Regula: vânzarea anonimă nu intră, factura la cerere intră

Vânzările cu amănuntul către persoane fizice neidentificate, pentru care se emite bon fiscal, nu generează obligație de e-Factura. Cumpărătorul anonim din magazin, plătit pe loc, nu produce un document care trebuie transmis prin sistemul național.

**În momentul în care clientul cere factură**, situația se schimbă: factura respectivă intră în sistem, prin exact același mecanism ca orice altă factură emisă — generare, validare la validatorul public ANAF, verificare că nu există deja o trimitere activă, apoi upload. Nu există o cale de emitere „mai simplă" pentru facturile emise la cererea clientului de la bonul fiscal — tehnic, e o factură ca oricare alta.

## Ce trebuie să ai pregătit

Pentru a emite factura la cerere, ai nevoie de datele de identificare ale clientului — dacă e persoană juridică, CUI-ul; dacă e persoană fizică, datele de identificare cerute de elementele obligatorii ale facturii. Fără aceste date complete, generarea XML poate fi blocată de reguli de completitudine (de exemplu, regula specifică sectorului din București, care nu permite emiterea cu o adresă incompletă — sistemul preferă să oprească trimiterea decât să trimită date presupuse).

## Ce se greșește în practică

- Se presupune că o factură emisă la cerere, după un bon fiscal, are alt regim de transmitere decât o factură obișnuită — nu are, trece prin același flux, cu același termen legal de transmitere.
- Se emite factura fără datele complete ale clientului, riscând blocaje la generare sau, mai rău, o factură incompletă transmisă efectiv.
- Se amână emiterea facturii cerute de client, tratând-o ca pe o formalitate opțională — odată cerută, factura intră sub aceleași obligații și termene ca oricare alta.

## Ce face iConta.eu

Nu tratează diferit o factură emisă la cererea clientului față de una emisă din start — trece prin același generator XML și prin aceleași patru verificări la trimitere (token activ, validare de structură, verificare anti-dublare, upload). Regulile de completitudine a datelor (de exemplu, sectorul pentru adresele din București) se aplică identic, indiferent de motivul pentru care s-a emis factura.

[iConta.eu](/)
