---
title: "Ce amendă se aplică pentru D390 depusă cu întârziere?"
description: "Amenda contravențională pentru nedepunerea la termen a declarației recapitulative D390 privind operațiunile intracomunitare, conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce amendă se aplică pentru D390 depusă cu întârziere?

Declarația recapitulativă D390 (livrări/achiziții/prestări intracomunitare) are un regim contravențional propriu, separat de sancțiunile pentru alte declarații. Nedepunerea ei la termen nu e o simplă „întârziere administrativă" — e o contravenție expres reglementată, cu amendă între limite fixe.

## Temeiul legal

::: ghid-temei
„ART. 337 Contravenții în cazul declarațiilor recapitulative
(1) Constituie contravenții următoarele fapte: a) nedepunerea la termenele prevăzute de lege a declarațiilor recapitulative reglementate de normele din Codul fiscal privind taxa pe valoarea adăugată; b) depunerea de declarații recapitulative incorecte ori incomplete.
(2) Contravențiile prevăzute la alin. (1) se sancționează astfel: a) cu amendă de la 1.000 lei la 5.000 lei în cazul săvârșirii faptei prevăzute la lit. a); b) cu amendă de la 500 lei la 1.500 lei în cazul săvârșirii faptei prevăzute la lit. b)."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 337 alin. (1), (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Din text rezultă câteva precizări utile:

- Pentru **nedepunerea la termen** a D390, amenda e cuprinsă între **1.000 și 5.000 lei** — indiferent de mărimea firmei sau de valoarea operațiunilor intracomunitare nedeclarate.
- Pentru **depunerea unei declarații incorecte sau incomplete** (dar depusă la termen), amenda e mai mică — între **500 și 1.500 lei** — deoarece fapta e considerată mai puțin gravă decât nedepunerea completă.
- Legea prevede și o cale de a evita sancțiunea: potrivit alin. (3) al aceluiași articol, nu se sancționează contravențional cel care **corectează** declarația recapitulativă până la termenul legal de depunere a următoarei declarații, dacă eroarea (declarație incorectă/incompletă) nu a fost deja constatată de organul fiscal, și nici cel care corectează declarația ulterior termenului ca urmare a unui fapt neimputabil.
- Aceeași structură de sancțiuni (1.000-5.000 lei pentru nedepunere, 500-1.500 lei pentru erori) se aplică, separat, și fișierului standard de control fiscal (SAF-T), la articolul imediat următor din lege.

## Ce se greșește în practică

- Se presupune că amenda pentru D390 e aceeași cu cea pentru alte declarații (D300, D112), fără să se verifice regimul contravențional specific de la art. 337.
- Nu se folosește fereastra de corectare fără sancțiune, prevăzută la alin. (3) — se lasă o eroare necorectată până la constatarea ei de organul fiscal, deși putea fi remediată fără amendă până la termenul următoarei declarații.
- Se confundă „declarație incorectă" (amendă mai mică, 500-1.500 lei) cu „nedepunere" (amendă mai mare, 1.000-5.000 lei), deși legea le tratează ca fapte contravenționale distincte.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează declarația D390 pe baza operațiunilor intracomunitare înregistrate (`core/d390.py`), cu module de clasificare și reconciliere (`core/d390_clasificare_api.py`, `core/d390_reconciliere.py`) care ajută la identificarea erorilor înainte de depunere. Aplicația **nu calculează și nu afișează amenzi contravenționale** și nu depune automat declarația la ANAF — urmărirea termenului de depunere și evitarea sancțiunilor de la art. 337, inclusiv corectarea din timp a eventualelor erori, rămân responsabilitatea contabilului.

[iConta.eu](/)
