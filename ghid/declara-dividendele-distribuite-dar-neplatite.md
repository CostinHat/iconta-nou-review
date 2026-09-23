---
title: "Cum se declară dividendele distribuite dar neplătite"
description: "Pașii pentru a nu pierde din D205 un dividend aprobat spre distribuire, dar pe care asociatul nu l-a încasat până la 31 decembrie."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se declară dividendele distribuite dar neplătite

Un dividend aprobat spre distribuire (înregistrat contabil, de regulă credit 457) rămâne o obligație de declarat chiar dacă asociatul nu a încasat efectiv suma până la sfârșitul anului.

## Temeiul legal

::: ghid-temei
"[...] În cazul dividendelor/câștigurilor obținute ca urmare a deținerii de titluri de participare, distribuite, dar care nu au fost plătite acționarilor/asociaților/investitorilor până la sfârșitul anului în care s-a aprobat distribuirea acestora, impozitul pe dividende/câștig se plătește până la data de 25 ianuarie inclusiv a anului următor distribuirii."
— Codul fiscal, art. 97 alin. (7) (`anaf_surse/cod_fiscal_227_2015_consolidat.txt:9470-9474`)
:::

Distribuirea (creditul contului 457) și plata (debitul contului 457) sunt două evenimente distincte în contabilitate, iar legea leagă obligația de declarare de momentul aprobării distribuirii, nu de momentul plății.

## Ce se greșește în practică

Situația cea mai frecventă: dividendul e aprobat și înregistrat contabil, dar declarantul așteaptă anul plății efective pentru a-l raporta în D205, considerând (greșit) că nu există obligație câtă vreme nu s-a plătit nimic.

## Ce face iConta.eu

Aici trebuie spusă exact limita actuală a aplicației: generatorul D205 (`core/d205.py`) construiește beneficiarii pornind de la suma efectiv plătită din contul 457; un dividend distribuit, dar cu plata zero la data generării, nu produce automat o linie în declarație — este un gol de conformitate cunoscut la nivel de produs, nu un caz acoperit implicit. Pe de altă parte, dacă dividendul a fost distribuit într-un an și plătit (integral sau eșalonat) în anul următor, iConta aplică deja corect cota fiscală în vigoare la data distribuirii (nu cea de la data plății), verificat prin teste dedicate. Concluzie practică: pentru dividendul distribuit dar rămas complet neplătit la 31 decembrie, interfața iConta nu oferă în acest moment o opțiune de adăugare manuală a beneficiarului la generarea D205 — obligația pentru anul aprobării distribuirii trebuie tratată de contabil separat de fluxul automat al aplicației.

[iConta.eu](/)
