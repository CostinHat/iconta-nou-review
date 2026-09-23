---
title: "Cum se declară dividendele când asociații au procente diferite?"
description: "Cum se distribuie proporțional dividendul brut între asociați cu cote de participare diferite, în vederea declarării D205."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară dividendele când asociații au procente diferite?

Când asociații nu dețin cote egale din capitalul social, dividendul brut trebuie împărțit proporțional cu procentul fiecăruia, iar D205 trebuie să reflecte exact această proporție pe fiecare beneficiar.

## Temeiul legal

::: ghid-temei
Descrierea funcționalității F029 (`/home/claude/iconta/FUNCTIONALITATI.csv`, rând F029): "impozit reținut la sursă (dividende), beneficiari cu cota pe an (8/10/16%), împărțire automată a dividendului brut pe asociați după cote, XML validat."
:::

Declarația D205 nu are un câmp separat pentru "procent" — ceea ce se raportează este suma efectivă (bază + impozit) alocată fiecărui beneficiar, rezultată din aplicarea procentului acestuia asupra dividendului brut distribuit/plătit.

## Ce se greșește în practică

O greșeală frecventă este împărțirea dividendului în părți egale între asociați, ignorând cotele reale de participare stabilite prin actul constitutiv, mai ales când acestea au fost modificate în timp (cesiuni de părți sociale).

## Ce face iConta.eu

Repository-ul D205 (`core/repo_d205.py`) citește cota fiecărui asociat direct din datele firmei și calculează automat, pentru fiecare, partea proporțională din dividendul înregistrat pe contul 457. Sumele rezultate (bază de impozitare și impozit) sunt cele efectiv aferente cotei fiecărui asociat, nu împărțite egal. Este responsabilitatea contabilului să se asigure că datele privind cotele de participare ale asociaților sunt actualizate la zi în aplicație înainte de generarea declarației, întrucât o cotă neactualizată produce o defalcare greșită între beneficiari.

[iConta.eu](/)
