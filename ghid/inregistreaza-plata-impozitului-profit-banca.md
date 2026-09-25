---
title: "Cum se înregistrează plata impozitului pe profit prin bancă?"
description: "Contul contabil 441 „Impozitul pe profit și alte impozite\", din planul de conturi general (OMFP 1802/2014), și înregistrarea plății prin contul bancar."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se înregistrează plata impozitului pe profit prin bancă?

Înregistrarea plății impozitului pe profit prin bancă se sprijină pe un cont contabil dedicat, prevăzut explicit în planul de conturi general aprobat prin reglementările contabile în vigoare.

## Temeiul legal

::: ghid-temei
„44. Bugetul statului, fonduri speciale și conturi asimilate
441. Impozitul pe profit și alte impozite"
— OMFP nr. 1.802/2014 (Reglementări contabile privind situațiile financiare anuale individuale și consolidate — Planul de conturi general), clasa 4, grupa 44 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Ce rezultă pentru înregistrarea contabilă:

- Obligația de plată a impozitului pe profit se reflectă în contul **441 „Impozitul pe profit și alte impozite"**, cont de pasiv, care se creditează cu impozitul datorat (calculat conform declarației D101) și se debitează la plata efectivă.
- Plata prin bancă se înregistrează prin nota contabilă **441 = 5121** („Conturi la bănci în lei"), reflectând ieșirea de disponibilități pentru stingerea obligației fiscale.
- Contul 441 este folosit atât pentru impozitul pe profit, cât și pentru „alte impozite" asimilate acestuia din grupa 44 a planului de conturi — analiticele distincte pe fiecare tip de obligație sunt o practică organizatorică a firmei, nu o cerință separată din text.

## Ce se greșește în practică

- Se înregistrează plata impozitului pe profit direct pe o cheltuială (contul 691 „Cheltuieli cu impozitul pe profit"), fără a trece prin contul de datorie 441 — asta denaturează atât rezultatul, cât și soldul obligațiilor fiscale ale firmei.
- Se amestecă în același analitic al contului 441 impozitul pe profit cu alte impozite fără legătură (de exemplu, taxe locale), ceea ce face dificilă reconcilierea cu declarația D101.
- Se înregistrează plata cu întârziere față de extrasul de cont bancar, ceea ce denaturează soldul contului 5121 la data raportării.

## Ce face iConta.eu

Verificat în cod: `core/d101.py` generează Declarația 101 (impozitul pe profit) din datele contabile ale firmei, iar `core/d101_reconciliere.py` recalculează independent baza contabilă a impozitului (veniturile și cheltuielile din clasele 6/7) pentru a o confrunta cu ce a generat calculul declarației, semnalând orice divergență; plata efectivă a impozitului pe profit prin bancă se înregistrează ca notă contabilă obișnuită (441=5121) în modulele de bancă ale aplicației, folosind planul de conturi OMFP 1802/2014.

[iConta.eu](/)
