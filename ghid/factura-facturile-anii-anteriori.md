---
title: "e-Factura pentru facturile din anii anteriori"
description: "Ce prevede OUG 120/2021 despre obligativitatea RO e-Factura și de ce ea nu se aplică retroactiv facturilor emise înainte de intrarea în vigoare a obligației."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# e-Factura pentru facturile din anii anteriori

Întrebarea dacă facturile din anii trecuți trebuie „trecute" acum prin sistemul RO e-Factura vine, de regulă, din confuzia dintre obligația de facturare curentă și arhivarea/regăsirea documentelor emise înainte ca ea să existe. Sistemul RO e-Factura e reglementat ca sistem de transmitere pentru facturi emise curent, nu ca arhivă retroactivă.

## Temeiul legal

::: ghid-temei
„(2) Sistemul naţional privind factura electronică RO e-Factura reprezintă ansamblul de principii, reguli şi aplicaţii informatice având drept scop primirea facturii electronice de la emitent [...], stocarea prin mijloace electronice a facturilor şi transmiterea către destinatar.
(3) Sistemul naţional privind factura electronică RO e-Factura devine operaţional în termen de maximum 30 de zile de la data intrării în vigoare a prezentei ordonanţe de urgenţă."
— OUG 120/2021, art. 3 alin. (2)-(3) (sursă: anaf_surse/oug_120_2021.txt)
:::

Ce rezultă, chiar dacă textul exact al momentelor de operaționalizare pentru fiecare categorie de contribuabili nu e reprodus integral aici:

- **RO e-Factura e un sistem de transmitere pentru facturi emise de la un anumit moment înainte**, stabilit succesiv prin acte normative (OUG 120/2021, cu extinderi ulterioare prin acte precum OUG 115/2023 pentru B2B general) — nu un mecanism de „reconstituire" a facturilor emise anterior devenirii lui obligatoriu.
- O factură emisă legal, într-un an în care RO e-Factura nu era încă obligatorie pentru relația respectivă (B2B, B2G sau B2C, fiecare cu momentul ei de intrare în obligativitate), **rămâne valabilă în forma emisă atunci** — nu trebuie „reemisă" sau transmisă retroactiv prin sistem doar pentru că sistemul a devenit între timp obligatoriu.
- Nevoia reală, în astfel de cazuri, e de regulă alta: regăsirea/arhivarea unei facturi vechi pentru control sau audit, nu transmiterea ei prin RO e-Factura — arhivarea documentelor contabile urmează regulile generale din Legea contabilității (82/1991), nu pe cele ale sistemului e-Factura.

**Limitare onestă:** sursele disponibile confirmă principiul (sistemul operează pentru facturi curente, de la un moment de intrare în vigoare) dar nu conțin, într-o formă citabilă verbatim aici, un text explicit care să spună „RO e-Factura nu se aplică retroactiv" — concluzia rezultă din structura obligației (moment de intrare în vigoare + operațiuni curente), nu dintr-o interdicție expresă de retroactivitate.

## Ce se greșește în practică

- Se încearcă „încărcarea" facturilor vechi în sistemul RO e-Factura, deși sistemul e construit pentru transmiterea facturilor la momentul emiterii, nu pentru arhivare retroactivă.
- Se confundă lipsa unei facturi din sistemul RO e-Factura cu nevalabilitatea ei — o factură emisă corect înainte de obligativitate rămâne un document fiscal valabil.
- Se ignoră faptul că momentul de la care RO e-Factura a devenit obligatorie diferă între relațiile B2G, B2B și B2C, tratând o singură dată-limită pentru toate situațiile.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **transmite prin RO e-Factura facturile emise curent din aplicație** (module `core/efactura_send.py`, `core/efactura_trimitere.py`), potrivit obligației aplicabile la data emiterii. Aplicația **nu retransmite prin sistem facturi vechi**, emise înainte de introducerea fluxului de e-Factura în iConta — acestea rămân în evidența contabilă, în forma în care au fost emise atunci.

[iConta.eu](/)
