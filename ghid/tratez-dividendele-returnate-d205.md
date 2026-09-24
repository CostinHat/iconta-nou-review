---
title: "Cum tratez dividendele returnate: D205"
description: "Dividendul interimar care depășește dividendul anual aprobat se restituie de asociat în 60 de zile; declararea acestei situații la D205 e o funcționalitate separată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum tratez dividendele returnate: D205

„Dividende returnate" apare cel mai adesea într-un singur context real: dividendul interimar distribuit trimestrial a fost mai mare decât dividendul anual aprobat ulterior, iar diferența trebuie restituită de asociat firmei.

## Temeiul legal

::: ghid-temei
„În cazul în care asociații sau acționarii datorează restituiri de dividende, în urma regularizării operate în situațiile financiare anuale, acestea se achită societății în termen de 60 de zile de la data aprobării situațiilor financiare anuale." — Legea 31/1990, art. 67 alin. (2^2)
:::

Restituirea apare la regularizarea de final de an: dividendul anual aprobat se compensează cu interimarul deja distribuit (457=463), iar dacă interimarul a fost mai mare, excesul se restituie de asociat prin 5121=456, în cel mult 60 de zile de la aprobarea situațiilor financiare anuale. După acest termen, asociatul datorează dobândă penalizatoare calculată conform art. 3 din OG 13/2011.

Separat de acest caz, dividendele plătite cu încălcarea regulilor de distribuire (alin. 2, 2^1, 2^2 sau 3) se restituie dacă societatea dovedește că asociatul a cunoscut sau trebuia să cunoască neregularitatea (art. 67 alin. 4), iar dreptul la acțiunea de restituire se prescrie în 3 ani de la data distribuirii (alin. 5).

## Ce se greșește în practică

Greșeala frecventă e confundarea „dividendului returnat" din regularizare (o consecință firească a distribuirii trimestriale) cu restituirea unui dividend plătit nelegal — cele două au temeiuri și regimuri diferite. O altă greșeală e tratarea restituirii ca simplă corecție a notei inițiale de dividend, fără o linie contabilă separată pentru suma restituită.

## Ce face iConta.eu

Pentru cazul obișnuit — exces al dividendului interimar față de cel anual aprobat — iConta calculează automat diferența de restituit și generează linia 5121=456, la regularizarea de final de an. Declararea acestei restituiri la D205 este o funcționalitate separată de decontările cu asociații; F039 pregătește nota contabilă a restituirii, dar mecanismul de completare a D205 nu face parte din acest modul și nu e detaliat aici. Pentru restituirea unui dividend plătit nelegal (art. 67 alin. 4), F039 nu are o funcție dedicată — aplicația generează doar nota standard de dividend/regularizare.

[iConta.eu](/)
