---
title: Cum verific vectorul fiscal al firmei înainte de depunerea declarațiilor?
description: Vectorul fiscal (regim, TVA, periodicitate, intracomunitar) se verifică pe ecranul Date firmă — un câmp necompletat lasă declarația aferentă gri, cu cauza afișată explicit.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum verific vectorul fiscal al firmei înainte de depunerea declarațiilor?

Înainte de a depune orice declarație, verifică cei patru parametri care decid ce se datorează: regimul fiscal, dacă firma e plătitoare de TVA (și periodicitatea), dacă are operațiuni intracomunitare — plus semaforul care arată exact ce lipsește.

## Temeiul legal

::: ghid-temei
Vectorul fiscal nu are un temei legal unic — cei patru atribute provin din articole diferite ale Codului fiscal: **regimul fiscal micro/profit** (art. 47, 52 CF), **calitatea de plătitor de TVA** (art. 316 CF), **periodicitatea decontului de TVA** (art. 322 CF) și **operațiunile intracomunitare** (art. 317 CF). În registrul intern al funcționalităților iConta, câmpul „Temei legal" asociat lui F100 e gol — fiecare atribut al vectorului are propriul temei, verificat separat.
:::

Verificarea practică începe cu cele patru câmpuri din Vector fiscal (ecranul Date firmă): regimul fiscal (micro/profit), dacă firma e plătitoare de TVA (și, dacă da, periodicitatea — lunară sau trimestrială), și dacă are operațiuni intracomunitare. Toate patru sunt obligatorii, fără valoare implicită tacită — dacă vreunul lipsește, vectorul e considerat „necompletat", iar declarațiile care depind de el apar gri în semafor, cu motivul explicit afișat, nu ca un simplu blocaj nemotivat.

Un al doilea nivel de verificare compară ce ai salvat local cu ce arată ANAF: dacă snapshotul TVA din ANAF diferă de ce ai bifat local, aplicația arată un semnal roșu (diferență), verde (coincid) sau gri (lipsă snapshot) — dar decizia de a corecta rămâne a ta, nu există un buton care schimbă automat regimul.

Un al treilea nivel privește operațiunile efective: dacă vectorul spune „fără operațiuni intracomunitare", dar aplicația găsește facturi IC reale, contradicția e semnalată explicit, cu recomandarea de a corecta vectorul — fără să blocheze automat generarea declarațiilor.

## Ce se greșește în practică

- Se presupune că lipsa unei erori la depunere înseamnă vector corect — semaforul poate arăta gri (necunoscut), nu neapărat o eroare blocantă, iar contabilul trebuie să observe activ starea.
- Se ignoră semnalul roșu de discrepanță TVA local vs. ANAF, presupunând că aplicația va corecta automat regimul — nu există o asemenea automatizare.
- Se lasă contradicția „fără operațiuni IC" vs. facturi IC reale nerezolvată, deși aplicația o semnalează explicit ca inconsistență de corectat în Vector fiscal.

## Ce face iConta.eu

Motorul din `core/control_fiscal_api.py` (funcția `declaratii_datorate`) traduce cei patru parametri ai vectorului, plus faptele reale (salariați, facturi IC), în lista de declarații datorate/scadente. Un atribut necompletat nu produce niciodată un „default tăcut" — declarația dependentă iese gri, cu cauza declarată explicit. Comparația live cu ANAF (roșu/verde/gri) e un semnal, nu un blocaj: salvarea rămâne posibilă chiar dacă diferă de ce arată ANAF, decizia finală fiind a contabilului.

[iConta.eu](/)
