---
title: "Când trebuie încetate contractele de muncă înainte de radiere?"
description: "Momentul legal în care contractele individuale de muncă încetează de drept la dizolvarea unei firme — și de ce, în practică, ele se închid de regulă mai devreme."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Când trebuie încetate contractele de muncă înainte de radiere?

Contractul individual de muncă nu încetează automat „înainte" de radiere — legea leagă încetarea de drept de momentul în care persoana juridică își încetează efectiv existența, adică radierea însăși. În practică, însă, contractele se închid de regulă mai devreme, prin concediere, pentru că activitatea (și implicit nevoia de personal) se oprește înaintea finalizării procedurii de lichidare.

## Temeiul legal

::: ghid-temei
„Articolul 56
Contractul individual de muncă încetează de drept: [...] c) ca urmare a dizolvării angajatorului persoana juridică, de la data la care persoana juridică îşi încetează existenta."
— Legea 53/2003 (Codul muncii), art. 56 lit. c) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

Ce rezultă din text:

- Încetarea **de drept** (automată, fără nicio formalitate de concediere) intervine abia „de la data la care persoana juridică își încetează existența" — adică la finalizarea procedurii de dizolvare/lichidare, moment care coincide practic cu radierea din registrul comerțului, nu cu o dată anterioară arbitrară.
- Până la acel moment, contractele de muncă rămân, din punct de vedere juridic, active — dacă angajatorul vrea să le încheie mai devreme (de exemplu la începutul procedurii de lichidare, când activitatea operațională se oprește), trebuie să folosească o procedură de concediere distinctă (concediere pentru motive care nu țin de persoana salariatului, legate de dizolvare/reorganizare), nu să aștepte încetarea de drept.
- Practic, majoritatea firmelor în lichidare încetează contractele de muncă **înainte** de radierea efectivă, exact pentru că activitatea nu mai continuă în etapa de valorificare a activelor și plată a datoriilor — dar aceasta e o decizie de concediere activă a angajatorului, cu propriile formalități și termene de preaviz, nu o consecință automată a legii.

## Ce se greșește în practică

- Se presupune că deschiderea procedurii de lichidare încetează automat toate contractele de muncă — încetarea de drept (art. 56 lit. c)) intervine abia la încetarea existenței persoanei juridice, nu la începutul lichidării.
- Se omit formalitățile de concediere (preaviz, decizie scrisă, motivare) atunci când contractele se închid înainte de radiere, tratând situația ca pe o încetare de drept care nu le-ar cere.
- Se continuă generarea de obligații salariale (și D112) după ce activitatea s-a oprit efectiv, doar pentru că radierea nu s-a finalizat încă — dacă totuși contractele nu au fost formal încetate, obligațiile legale față de salariați rămân active.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu am identificat în cod** o funcționalitate care să coordoneze automat încetarea contractelor de muncă cu procedura de lichidare/radiere a firmei. Modulul `core/lichidare.py` acoperă motorul contabil al lichidării (valorificarea activelor, partajul, impozitul pe câștigul asociaților), nu gestiunea resurselor umane; aplicația oferă evidența contabilă generală și statul de plată, în care contabilul înregistrează manual încetarea fiecărui contract, pe baza deciziei de concediere emise de angajator.

[iConta.eu](/)
