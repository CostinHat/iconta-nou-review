---
title: Cum detectez facturile duplicate descărcate din SPV?
description: Aplicația nu semnalează automat rândurile duplicate din lista de facturi de validat — se recunosc manual, după număr, furnizor și dată identice, înainte de a valida oricare dintre ele.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum detectez facturile duplicate descărcate din SPV?

Din când în când, în lista de facturi primite de validat pot apărea două rânduri care par să descrie aceeași factură. Nu e o eroare de aplicație, dar merită înțeles de ce apare și cum se recunoaște.

## Temeiul legal

::: ghid-temei
„Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura."

— OUG nr. 120/2021, art. 4 alin. (7)
:::

Fiindcă sistemul ANAF poate genera mesaje separate pentru aceeași operațiune (de exemplu la o retransmitere), fiecare astfel de mesaj devine „disponibil pentru descărcare” de sine stătător — și aplicația îl aduce ca rând separat, pentru că nu are cum să știe, doar din identificatorul mesajului, că se referă la o factură deja cunoscută.

## Cum recunoști un duplicat

Semnul clar e două rânduri în lista de validat cu **același furnizor, același număr de factură și aceeași dată de emitere** — eventual cu sume identice. Asta arată că e vorba, cel mai probabil, de două mesaje ANAF diferite pentru practic aceeași factură (de exemplu o retransmitere din partea furnizorului), nu de două facturi distincte care coincid întâmplător.

Motivul tehnic: deduplicarea de la descărcare funcționează pe identificatorul de mesaj ANAF, nu pe conținutul facturii — dacă ANAF a atribuit două identificatoare diferite aceleiași operațiuni, aplicația nu are cum să le recunoască drept „același lucru” înainte de validare.

## Ce faci, concret

Verifică vizual numărul, furnizorul și data — dacă coincid, validează o singură dată (a doua validare oricum nu ar crea o cheltuială nouă, ci ar lega factura de cea deja înregistrată). Rândul rămas nevalidat îl poți respinge, cu un motiv scurt ca „duplicat, deja validat celălalt mesaj” — rândul respins nu se șterge, rămâne în istoric cu motivul consemnat.

## Ce se greșește în practică

- Se lasă rândurile duplicate nevalidate la nesfârșit în listă, în loc de a le respinge explicit odată identificate.
- Se presupune că aplicația marchează automat vizual duplicatele — nu există, la acest moment, o astfel de evidențiere automată în listă.
- Se compară doar suma facturii, ignorând numărul și data — două facturi diferite pot avea întâmplător aceeași sumă.

## Ce face iConta.eu

Aplicația nu afișează încă o marcare automată a rândurilor potențial duplicate în lista de validat — recunoașterea vizuală (același furnizor, număr, dată) rămâne, la acest moment, în sarcina contabilului. Ce garantează aplicația e că nu poți crea din greșeală o a doua cheltuială pentru aceeași factură: verificarea pe număr + furnizor + dată la validare oprește asta, indiferent câte rânduri „gemene” există în listă.

[iConta.eu](/)
