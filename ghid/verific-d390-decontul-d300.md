---
title: "Cum verific D390 cu decontul D300?"
description: Pentru operațiunile intracomunitare reclasificate, D390 și D300 nu se compară printr-un buton dedicat — coerența e garantată structural, dintr-o singură sursă de date citită identic de ambele declarații.
published: 2026-09-23
modified: 2026-10-13
poarta: v1
---

# Cum verific D390 cu decontul D300?

Nu există în panoul de declarații un buton „compară D390 cu D300". Mecanismul real e altul, și mai puternic decât o simplă verificare: pentru operațiunile reclasificate, coerența dintre cele două declarații e imposibil de rupt, pentru că se scriu dintr-o singură sursă.

## Mecanismul: o sursă unică, nu o comparație

Reclasificările bun-vs-serviciu ale operațiunilor intracomunitare (livrare sau achiziție) se scriu într-un singur tabel, „reclasificările D390 (Declarații)”, populat din panoul D390. Acest tabel e **citit identic** de ambele generatoare de declarație: D300 prin `_incarca_reclasificari` → „reclasificările”, D390 prin `calculeaza` → „reclasificările”, aceeași funcție.

Efectul, confirmat prin teste interne: după reclasificarea unei livrări IC emise ca „P" (serviciu), baza de la rândul 3 din D300 (cu subrândul 3.1, servicii intracomunitare) devine egală cu suma serviciilor „P" din rezumatul D390, iar baza de la rândul 1 (bunuri) dispare din D300 — operațiunea e **mutată**, nu adăugată în plus. Simetric, pentru achizițiile IC reclasificate „S" (serviciu): baza de la rândul 7 din D300 (cu subrândul 7.1) egală cu suma „S" din D390, cu oglinda deductibilă de la rândul 22 (net zero).

Pentru că o singură scriere în „reclasificările D390 (Declarații)” schimbă simultan ambele declarații, o divergență între ele, pentru operațiunile reclasificate, e structural imposibilă — nu pentru că există un instrument care o verifică și o corectează, ci pentru că ambele citesc aceeași sursă.

## Ce nu există

Nu e un ecran sau o rută API dedicată „verifică D390 vs D300" în sursele citite — nici în panoul manual „Rând manual D300”, nici altundeva în motorul D300. Verificarea/comparația celor două declarații, ca funcționalitate separată pe care contabilul o declanșează, e documentată în alt loc din aplicație, nu face parte din „Rând manual D300”.

## Ce se greșește în practică

Se caută un buton dedicat „compară D390 cu D300" în ecranul de declarații al „Rând manual D300” — nu există unul aici; coerența pentru operațiunile reclasificate e garantată de motor prin sursa unică de date, nu printr-o acțiune de verificare separată.

## Ce face iConta.eu

Pentru operațiunile reclasificate prin panoul D390, D300 citește aceeași sursă („reclasificările D390 (Declarații)”) prin aceeași funcție folosită și de D390 — coerența dintre cele două declarații e structurală, nu rezultatul unei verificări separate din „Rând manual D300”. O funcționalitate dedicată de comparație/verificare a celor două declarații e documentată separat.

[iConta.eu](/)
