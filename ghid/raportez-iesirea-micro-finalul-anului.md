---
title: "Cum raportez ieșirea din micro la finalul anului"
description: "Regulile de ieșire din sistemul de impunere pe veniturile microîntreprinderilor în cursul anului fiscal, atunci când firma depășește pragul de venituri, potrivit Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum raportez ieșirea din micro la finalul anului

Ieșirea din regimul micro nu așteaptă închiderea anului fiscal — legea o declanșează chiar din trimestrul în care firma depășește pragul, nu retroactiv, de la 1 ianuarie.

## Temeiul legal

::: ghid-temei
„(1) Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită. [...] (5) Limitele fiscale prevăzute la alin. (1) se verifică pe baza veniturilor înregistrate cumulat de la începutul anului fiscal. Cursul de schimb pentru determinarea echivalentului în euro este cel valabil la închiderea exercițiului financiar precedent."
— Legea nr. 227/2015 (Codul fiscal), art. 52 alin. (1) și (5) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce înseamnă asta pentru raportare:

- Depășirea plafonului de **100.000 euro** se verifică prin cumularea veniturilor **de la începutul anului fiscal**, nu izolat, pe fiecare trimestru — de îndată ce cumulul depășește pragul, firma devine plătitoare de impozit pe profit din acel trimestru.
- Cursul de schimb folosit pentru echivalentul în euro este cel valabil **la închiderea exercițiului financiar precedent** — nu cursul zilei în care are loc încasarea care declanșează depășirea.
- Calculul și plata impozitului pe profit, pentru trimestrul în care s-a depășit pragul, se fac luând în calcul veniturile și cheltuielile realizate **începând cu trimestrul respectiv**, nu retroactiv, de la 1 ianuarie.
- Legea prevede și alte cauze de ieșire forțată în cursul anului, distincte de depășirea plafonului: nedepunerea la termen a situațiilor financiare anuale (alin. (2)) sau pierderea condiției de salariat (alin. (3)).

## Ce se greșește în practică

- Se așteaptă finalul anului fiscal pentru a „raporta" ieșirea din micro, deși legea o declanșează automat din trimestrul depășirii, cu obligații de declarare distincte pentru impozitul pe profit începând din acel moment.
- Se folosește cursul de schimb din ziua încasării care a dus la depășirea plafonului, în loc de cursul valabil la închiderea exercițiului financiar precedent, așa cum cere legea.
- Se ignoră celelalte cauze de ieșire forțată din micro (nedepunerea situațiilor financiare, pierderea condiției de salariat), tratând depășirea plafonului de venituri drept singurul motiv posibil.

## Ce face iConta.eu

La data acestui ghid, iConta.eu urmărește regimul fiscal setat în profilul firmei (`core/vector_fiscal_api.py`) și generează declarațiile corespunzătoare regimului activ, dar **nu monitorizează automat** cumulul veniturilor firmei față de pragul de 100.000 euro și nu alertează contabilul la momentul depășirii. Verificarea plafonului și schimbarea regimului fiscal, cu trecerea corectă la calculul impozitului pe profit din trimestrul relevant, rămân operațiuni pe care contabilul le identifică și le introduce manual în aplicație.

[iConta.eu](/)
