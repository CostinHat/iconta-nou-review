---
title: "Cum corectez o eroare într-un D300 deja depus?"
description: "Procedura legală de corectare a unui decont de TVA deja depus, prin declarație rectificativă, și cum ajută controlul încrucișat D390 vs D300 din iConta.eu la depistarea unei asemenea erori."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum corectez o eroare într-un D300 deja depus?

Odată depus, un decont de TVA (D300) nu se poate „edita" — corectarea lui se face printr-o declarație rectificativă, depusă separat, care înlocuiește datele greșite. Procedura e generală, valabilă pentru orice declarație fiscală, cu o particularitate specifică pentru erorile materiale din decontul de TVA.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale. [...] (3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative. (4) în cazul taxei pe valoarea adăugată, corectarea erorilor din deconturile de taxă se realizează potrivit prevederilor Codului fiscal. Erorile materiale din decontul de taxă pe valoarea adăugată se corectează potrivit procedurii aprobate prin ordin al președintelui A.N.A.F."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1), (3) și (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Câteva limite importante ale dreptului de corectare, din același articol:

- Declarația de impunere **nu mai poate fi corectată** după anularea rezervei verificării ulterioare (art. 105 alin. (5)), cu excepțiile explicite de la alin. (6) — de exemplu o hotărâre judecătorească definitivă care modifică baza de impozitare.
- Dacă în timpul unei inspecții fiscale contribuabilul depune sau corectează declarația pentru perioada aflată sub inspecție, corecția **nu e luată în considerare** de organul fiscal (art. 105 alin. (8)).
- Erorile pur materiale (de exemplu o cifră scrisă greșit, fără impact pe fond) se corectează printr-o procedură separată, aprobată prin ordin ANAF, distinctă de rectificativă.

## Ce se greșește în practică

- Se încearcă o „ștergere" sau o reintroducere a decontului original, în loc de depunerea unei declarații rectificative — mecanismul legal e strict înlocuirea prin rectificativă, nu editarea celei vechi.
- Se ajustează un cont contabil ca declarația să „iasă corectă" retroactiv, în loc să se depună efectiv rectificativa — o corecție contabilă fără declarație rectificativă corespunzătoare nu rezolvă neconcordanța față de ANAF.
- Se confundă o eroare materială (corectabilă rapid, prin procedura specială ANAF) cu o eroare de fond în baza de impozitare (care necesită rectificativă completă, cu efect asupra sumei de plată).

## Ce face iConta.eu

iConta.eu nu are, în această versiune, o funcție dedicată de „editare a unui D300 deja depus" sau de generare automată a unei rectificative — corectarea propriu-zisă a declarației depuse e o procedură separată de depunere, care nu a fost obiectul acestei cercetări asupra codului aplicației.

Ce ajută efectiv la **depistarea** unei asemenea erori este funcționalitatea **F163 — Control încrucișat D390 vs. evidență/D300** (`core/control_incrucisat.py`), din ecranul Control fiscal → „Declarație vs contabilitate". Motorul compară, pe fiecare perioadă, baza declarată în D390 (livrări/achiziții intracomunitare) cu rândurile R1_1/R5_1 ale D300-ului **efectiv depus prin aplicație** — dacă declarația la VIES (D390) arată o sumă pe care D300 depus n-o reflectă, constatarea iese pe roșu, cu un remediu sugerat: fie rectificativă D300, fie corectarea D390, decizia rămânând la contabil. Această comparație acoperă strict rândurile intracomunitare (R1_1/R5_1) — nu verifică alte tipuri de erori din D300 (de exemplu TVA deductibilă greșit calculată pe achiziții interne) și nu urmărește dacă decontul a fost efectiv validat de ANAF, verificare care ar necesita conectarea directă la SPV.

[iConta.eu](/)
