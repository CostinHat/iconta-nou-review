---
title: "Cât timp rămân facturile disponibile pentru descărcare în SPV?"
description: "Ce spune legea despre disponibilitatea facturilor RO e-Factura și de ce arhivarea proprie, de minimum 5 ani, rămâne obligația firmei, conform OUG 120/2021 și Legii contabilității."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cât timp rămân facturile disponibile pentru descărcare în SPV?

Actele normative din acest corpus nu conțin un termen explicit privind numărul de zile în care o factură rămâne disponibilă pentru descărcare în sistemul RO e-Factura — acesta e un parametru tehnic-operațional al platformei ANAF, nu o regulă fixată prin lege sau ordin identificată în sursele verificate aici. Ce e sigur, în schimb, e obligația legală independentă a firmei de a-și arhiva propriile documente justificative, care nu depinde de cât timp le păstrează ANAF în portal.

## Temeiul legal

::: ghid-temei
„(7) Data comunicării facturii electronice către destinatar se consideră data la care factura electronică este disponibilă acestuia pentru descărcare din sistemul naţional privind factura electronică RO e-Factura."
— OUG 120/2021, art. 4 alin. (7) (sursă: anaf_surse/oug_120_2021.txt)

„Registrele de contabilitate obligatorii și documentele justificative care stau la baza înregistrărilor în contabilitatea financiară se păstrează în arhiva persoanelor prevăzute la art. 1 timp de 5 ani calculați de la data de 1 iulie a anului următor celui încheierii exercițiului financiar în care au fost întocmite, inclusiv pentru statele de salarii."
— Legea 82/1991, art. 25 (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Ce se poate afirma cu certitudine, pe baza acestor două texte:

- Legea leagă momentul **comunicării** facturii de momentul la care ea devine disponibilă pentru descărcare (art. 4 alin. (7)) — dar nu am identificat, în sursele consultate, un text care să stabilească explicit **până când** rămâne factura accesibilă în platformă pentru redescărcare ulterioară.
- Independent de politica tehnică a platformei RO e-Factura, firma are obligația legală, de sine stătătoare, de a păstra facturile ca documente justificative timp de **5 ani**, calculați de la 1 iulie a anului următor încheierii exercițiului financiar în care au fost întocmite (Legea 82/1991, art. 25).
- Practic, disponibilitatea temporară a facturii în portalul ANAF nu poate fi singura sursă de arhivare a firmei — indiferent cât timp rămâne accesibilă acolo, obligația de păstrare pe cei 5 ani rămâne a firmei, care trebuie să descarce și să-și constituie propria arhivă.

## Ce se greșește în practică

- Se contează pe SPV ca arhivă permanentă pentru facturi, fără o descărcare și o arhivare proprie, ceea ce expune firma la riscul de a nu avea acces la documentul justificativ dacă platforma nu îl mai afișează.
- Se confundă termenul de arhivare legală (5 ani, Legea 82/1991) cu o eventuală fereastră tehnică de descărcare din SPV — sunt lucruri diferite, chiar dacă amândouă privesc "cât timp am acces la factură".
- Se amână descărcarea facturilor primite prin RO e-Factura, presupunând că vor rămâne oricând disponibile — fără un temei legal confirmat pentru această presupunere, riscul practic e real.

## Ce face iConta.eu

iConta.eu descarcă automat, printr-un fir dedicat conectat la conectorul SPV/ANAF, facturile primite prin RO e-Factura de la furnizori, le inserează ca ciornă în evidența proprie și le păstrează în baza de date a firmei — astfel încât arhivarea nu depinde de fereastra tehnică de disponibilitate din portalul ANAF. Facturile trec printr-un proces de validare manuală (four-eyes) înainte de a fi asociate unei cheltuieli.

[iConta.eu](/)
