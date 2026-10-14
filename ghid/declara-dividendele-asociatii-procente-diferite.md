---
title: "Cum se declară dividendele când asociații au procente diferite?"
description: "Cum se distribuie proporțional dividendul brut între asociați cu cote de participare diferite, în vederea declarării D205."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum se declară dividendele când asociații au procente diferite?

Când asociații nu dețin cote egale din capitalul social, dividendul brut trebuie împărțit proporțional cu procentul fiecăruia, iar D205 trebuie să reflecte exact această proporție pe fiecare beneficiar.

Declarația D205 nu are un câmp separat pentru "procent" — ceea ce se raportează este suma efectivă (bază + impozit) alocată fiecărui beneficiar, rezultată din aplicarea procentului acestuia asupra dividendului brut distribuit/plătit.

## Temeiul legal

::: ghid-temei
„Cota-parte din profit ce se plătește fiecărui asociat constituie dividend. (2) Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social vărsat, opțional trimestrial pe baza situațiilor financiare interimare și anual, după regularizarea efectuată prin situațiile financiare anuale, dacă prin actul constitutiv nu se prevede altfel.”
— Legea nr. 31/1990 privind societățile, art. 67 alin. (1) și (2) (sursă: [Legea nr. 31/1990 privind societățile](https://legislatie.just.ro/Public/DetaliiDocument/798))

„Plătitorii de venituri cu regim de reținere la sursă a impozitelor au obligația să depună o declarație privind calcularea și reținerea impozitului pentru fiecare beneficiar de venit la organul fiscal competent, până în ultima zi a lunii februarie inclusiv a anului curent pentru anul expirat [...]”
— Codul fiscal, art. 132 alin. (2) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Ce se greșește în practică

O greșeală frecventă este împărțirea dividendului în părți egale între asociați, ignorând cotele reale de participare stabilite prin actul constitutiv, mai ales când acestea au fost modificate în timp (cesiuni de părți sociale).

## Ce face iConta.eu

Repository-ul D205 citește cota fiecărui asociat direct din datele firmei și calculează automat, pentru fiecare, partea proporțională din dividendul înregistrat pe contul 457. Sumele rezultate (bază de impozitare și impozit) sunt cele efectiv aferente cotei fiecărui asociat, nu împărțite egal. Este responsabilitatea contabilului să se asigure că datele privind cotele de participare ale asociaților sunt actualizate la zi în aplicație înainte de generarea declarației, întrucât o cotă neactualizată produce o defalcare greșită între beneficiari.

[iConta.eu](/)
