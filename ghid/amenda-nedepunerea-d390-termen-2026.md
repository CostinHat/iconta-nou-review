---
title: "Amenda pentru nedepunerea D390 la termen: cât este 2026"
description: "Amenzile prevăzute de Codul de procedură fiscală pentru nedepunerea la termen a declarației recapitulative D390 privind operațiunile intracomunitare, valabile în 2026."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amenda pentru nedepunerea D390 la termen: cât este 2026

D390 nu e o declarație oarecare din perspectiva sancțiunilor — Codul de procedură fiscală îi dedică un articol separat, distinct de regimul general al contravențiilor fiscale, cu amenzi proprii pentru nedepunere și, separat, pentru depunerea unei declarații incorecte sau incomplete.

## Temeiul legal

::: ghid-temei
„Constituie contravenții următoarele fapte: a) nedepunerea la termenele prevăzute de lege a declarațiilor recapitulative reglementate de normele din Codul fiscal privind taxa pe valoarea adăugată; b) depunerea de declarații recapitulative incorecte ori incomplete.
(2) Contravențiile prevăzute la alin. (1) se sancționează astfel: a) cu amendă de la 1.000 lei la 5.000 lei în cazul săvârșirii faptei prevăzute la lit. a); b) cu amendă de la 500 lei la 1.500 lei în cazul săvârșirii faptei prevăzute la lit. b).
(3) Nu se sancționează contravențional: a) persoanele care corectează declarația recapitulativă până la termenul legal de depunere a următoarei declarații recapitulative, dacă fapta prevăzută la alin. (1) lit. b) nu a fost constatată de organul fiscal anterior corectării; b) persoanele care, ulterior termenului legal de depunere, corectează declarațiile ca urmare a unui fapt neimputabil persoanei impozabile."
— Legea 207/2015, art. 337 (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Structura sancțiunilor, exactă:

- **Nedepunerea la termen** a D390 — amendă de **1.000 – 5.000 lei**.
- **Depunerea unei declarații incorecte sau incomplete** — amendă mai mică, **500 – 1.500 lei**, sancțiune distinctă de cea pentru nedepunere.
- Legea prevede și o **cauză de neaplicare a sancțiunii**: dacă se corectează declarația recapitulativă până la termenul de depunere a următoarei D390, iar organul fiscal nu constatase deja fapta, contravenția nu se sancționează. La fel, dacă corectarea ulterioară termenului se datorează unei cauze neimputabile persoanei impozabile.
- Sursele disponibile nu conțin, la art. 337, o actualizare explicită specifică anului 2026 a cuantumurilor amenzilor — valorile citate sunt cele din forma consolidată a Legii 207/2015 aplicabilă la data acestui ghid.

## Ce se greșește în practică

- Se aplică aceeași amendă pentru nedepunere și pentru depunerea incorectă — sunt praguri diferite: 1.000-5.000 lei pentru nedepunere, 500-1.500 lei pentru declarație incorectă/incompletă.
- Se presupune că orice corectare ulterioară a D390 e sancționabilă automat — legea exceptează explicit corectarea făcută înainte de termenul următoarei declarații recapitulative, dacă organul fiscal nu constatase deja eroarea.
- Se ignoră termenul de referință pentru „corectare la timp" — nu e un număr fix de zile, ci „până la termenul legal de depunere a următoarei declarații recapitulative", care variază după frecvența de depunere a firmei (lunară/trimestrială).

## Ce face iConta.eu

iConta.eu generează declarația D390 pe baza operațiunilor intracomunitare clasificate automat din facturile emise și primite (`core/d390.py`), inclusiv calculul, validarea și construirea fișierului XML pentru depunere. La data acestui ghid, aplicația **nu calculează și nu afișează cuantumul amenzii aplicabile** pentru o eventuală nedepunere sau depunere incorectă — urmărirea termenului de depunere și evitarea sancțiunilor contravenționale de la art. 337 rămân, la acest moment, responsabilitatea contabilului, aplicația oferind doar instrumentul de calcul și generare a declarației.

[iConta.eu](/)
