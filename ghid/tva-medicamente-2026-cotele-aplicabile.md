---
title: "TVA pentru medicamente 2026: cotele aplicabile"
description: Medicamentele de uz uman intră la cota redusă de 11%, fără distincție între cele compensate și cele eliberate fără prescripție — dar suplimentele alimentare, deși vândute tot în farmacie, rămân explicit la cota standard de 21%.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# TVA pentru medicamente 2026: cotele aplicabile

Livrarea de medicamente de uz uman beneficiază de cota redusă de TVA de 11%, ca literă separată în lista limitativă a art. 291 din Codul fiscal — nu ca parte a categoriei generale „alimente". Legea nu face distincție între medicamentele eliberate pe bază de prescripție (compensate sau nu) și cele eliberate liber (OTC): toate intră la 11%, atâta timp cât sunt „medicamente de uz uman".

## Temeiul legal

::: ghid-temei
Cota redusă de 11% se aplică pentru „livrarea de medicamente de uz uman" — Codul fiscal, art. 291 alin. (2) lit. a).
:::

## Ce acoperă și ce nu acoperă litera a)

Textul de lege vorbește explicit despre medicamente **de uz uman** — nu menționează medicamentele de uz veterinar ca fiind incluse la această literă. Medicamentele veterinare nu sunt tratate de art. 291 alin. (2) lit. a); dacă se încadrează la altă categorie de pe listă (de exemplu, ca produs pentru uz în agricultură/creșterea animalelor, la o altă literă), cota se determină după acea categorie, nu automat prin analogie cu medicamentele de uz uman.

De asemenea, legea nu condiționează cota redusă de statutul de „medicament compensat" sau de existența unei rețete — orice produs cu statut legal de medicament de uz uman intră la 11%, indiferent de canalul de eliberare.

## Ce se greșește în practică

- Se confundă „medicament" cu „supliment alimentar" — suplimentele alimentare, definite de Legea nr. 56/2021, sunt **excluse explicit** de la cota redusă (art. 291 alin. (2) lit. b) pct. 4), chiar dacă se vând în aceeași farmacie, adesea pe același raft cu medicamentele. Cota corectă pentru suplimente e 21%, nu 11%.
- Se aplică cota standard doar medicamentelor eliberate fără prescripție, din prezumția greșită că numai cele compensate au cotă redusă — legea nu face această distincție.
- Se aplică 11% și produselor cosmetice, dermato-cosmetice sau dispozitivelor medicale vândute în farmacie — acestea nu sunt „medicamente" în sensul art. 291 alin. (2) lit. a) și rămân, ca regulă, la cota standard, dacă nu se încadrează la altă categorie de pe listă.

## Ce face iConta.eu

`core/cote_tva.py` include categoria „medicamente" în `CATEGORII_11`, pe litera a) din art. 291 alin. (2). Suplimentele alimentare (Legea 56/2021) apar explicit în `EXCEPTII_21`, tocmai pentru a nu fi confundate cu medicamentele la clasificarea automată a liniei de factură. Dacă motorul de potrivire nu poate stabili cu certitudine dacă un produs e medicament, supliment sau alt tip de bun (de exemplu, dintr-o denumire comercială ambiguă), aplicația nu presupune tăcut o cotă — răspunde cu un statut de cotă nedeterminată, care cere o clasificare manuală înainte de emiterea facturii.

[iConta.eu](/)
