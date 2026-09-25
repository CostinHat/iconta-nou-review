---
title: "Când trece o microîntreprindere la impozit pe profit în 2026?"
description: "Situațiile în care o microîntreprindere devine, în cursul anului 2026, plătitoare de impozit pe profit, conform art. 52 din Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când trece o microîntreprindere la impozit pe profit în 2026?

Trecerea de la impozitul pe veniturile microîntreprinderilor la impozitul pe profit nu se întâmplă doar la schimbarea anului fiscal. Legea prevede patru situații distincte în care o microîntreprindere iese din sistem chiar în cursul anului, fiecare cu propriul moment de la care se calculează impozitul pe profit.

## Temeiul legal

::: ghid-temei
„(1) Dacă în cursul unui an fiscal o microîntreprindere realizează venituri mai mari de 100.000 euro, aceasta datorează impozit pe profit începând cu trimestrul în care s-a depășit această limită.
(2) În cazul în care, în cursul unui an fiscal, o microîntreprindere nu a depus în termen situațiile financiare anuale pentru exercițiul financiar precedent anului fiscal respectiv, dacă avea această obligație potrivit legii, microîntreprinderea datorează impozit pe profit începând cu trimestrul în care nu mai este îndeplinită această condiție.
(3) În cazul în care, în cursul unui an fiscal, o microîntreprindere nu mai îndeplinește condiția prevăzută la art. 47 alin. (1) lit. g) [are cel puțin un salariat], microîntreprinderea datorează impozit pe profit începând cu trimestrul următor celui în care a încetat raportul de muncă. [...] În cazul în care, în acest termen [30 de zile] nu se angajează un nou salariat, microîntreprinderea datorează impozit pe profit începând cu trimestrul următor celui în care a încetat raportul de muncă.
(4) Microîntreprinderile care în cursul unui trimestru încep să desfășoare activități dintre cele prevăzute de art. 47 alin. (3) lit. f)-i) [domeniul bancar, asigurări/reasigurări și piața de capital, jocuri de noroc, explorare/exploatare petrol și gaze] datorează impozit pe profit începând cu trimestrul respectiv."
— Legea 227/2015, art. 52 alin. (1)-(4) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cele patru trigger-e, aplicabile independent unul de altul:

- **Depășirea plafonului de 100.000 euro** (redus de la 500.000 euro prin OUG 8/2026, în vigoare de la 25.02.2026) — impozit pe profit din trimestrul depășirii, calculat cumulat de la începutul anului.
- **Nedepunerea la termen a situațiilor financiare anuale** — dacă firma avea obligația de a le depune și nu a făcut-o, trece la profit din trimestrul în care termenul a expirat.
- **Pierderea singurului salariat** — dacă nu se angajează un nou salariat în 30 de zile, impozitul pe profit se datorează din trimestrul următor încetării raportului de muncă.
- **Începerea unei activități excluse** (bancar, asigurări/reasigurări, piața de capital, jocuri de noroc, explorare petrol/gaze) — impozit pe profit chiar din trimestrul în care începe activitatea respectivă.

## Ce se greșește în practică

- Se așteaptă finalul anului fiscal pentru a face trecerea, deși legea cere schimbarea „începând cu trimestrul" respectiv, nu de la 1 ianuarie anul următor.
- Se confundă termenul de 30 de zile pentru reangajare (aplicabil doar la microîntreprinderile cu un singur salariat) cu o regulă generală valabilă pentru orice pierdere de personal.
- Se ignoră plafonul verificat cumulat de la începutul anului, calculându-se depășirea doar pe baza veniturilor unui singur trimestru.

## Ce face iConta.eu

iConta.eu calculează impozitul pe profit trimestrial pe baza reală a rezultatului fiscal (venituri minus cheltuieli, nu venituri brute), inclusiv cumulat de la începutul anului conform art. 41 din Codul fiscal — motorul D100 al aplicației a fost corectat explicit pentru a nu confunda „venituri × cotă" cu „profit × cotă". Pentru regimul micro, baza de calcul (venituri din orice sursă, cu ajustările din art. 53) este de asemenea implementată. La data acestui ghid, aplicația nu are însă un declanșator automat care să detecteze depășirea plafonului de 100.000 euro sau pierderea condiției de salariat și să comute singură profilul firmei de la micro la profit — trecerea rămâne o decizie pe care contabilul o marchează manual în aplicație, pe baza urmăririi celor patru situații de mai sus.

[iConta.eu](/)
