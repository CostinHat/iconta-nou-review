---
title: "Cum se amortizează investițiile efectuate într-o clădire proprie?"
description: "Regimul fiscal al investițiilor ulterioare care majorează valoarea unei clădiri aflate în proprietatea firmei, conform art. 28 din Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se amortizează investițiile efectuate într-o clădire proprie?

O investiție într-o clădire deja existentă în patrimoniul firmei (renovare majoră, extindere, modernizare) nu se tratează ca o cheltuială curentă, dacă majorează valoarea sau prelungește viața utilă a clădirii — Codul fiscal o consideră mijloc fix amortizabil de sine stătător.

## Temeiul legal

::: ghid-temei
„(3) Sunt, de asemenea, considerate mijloace fixe amortizabile: [...]
d) investițiile efectuate la mijloacele fixe existente, sub forma cheltuielilor ulterioare realizate în scopul îmbunătățirii parametrilor tehnici inițiali și care conduc la obținerea de beneficii economice viitoare, prin majorarea valorii mijlocului fix;"
— Legea 227/2015 (Codul fiscal), art. 28 alin. (3) lit. d) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Condiția-cheie e dublă, nu doar una: investiția trebuie (1) să îmbunătățească parametrii tehnici inițiali ai clădirii **și** (2) să conducă la beneficii economice viitoare, prin majorarea valorii mijlocului fix. Din combinarea acestei condiții cu regulile generale de amortizare rezultă:

- **Investiția se amortizează separat**, ca mijloc fix distinct sau ca majorare a valorii clădirii existente, nu se deduce integral, dintr-o dată, ca și cheltuială curentă de întreținere.
- **Durata de amortizare** urmează regulile generale de la art. 28 — pentru clădiri, intervalele minime-maxime din Catalogul privind clasificarea și duratele normale de funcționare a mijloacelor fixe (aprobat prin HG 2139/2004); de exemplu, clădirile industriale au o durată normală de funcționare de 40-60 de ani, iar cele agrozootehnice de 24-36 de ani — durata exactă depinde de categoria concretă a clădirii.
- **Distincția critică față de o simplă reparație/întreținere**: dacă lucrarea doar readuce clădirea la parametrii inițiali, fără să îi majoreze valoarea sau să îi prelungească durata de utilizare (o reparație curentă, o zugrăveală, o înlocuire identică), cheltuiala e deductibilă integral, direct, ca și cheltuială de exploatare — nu intră sub incidența art. 28 alin. (3) lit. d).
- Amortizarea fiscală a investiției pornește, ca pentru orice mijloc fix, din luna următoare punerii în funcțiune (art. 28 alin. 12 lit. a), moment care trebuie documentat separat de data punerii în funcțiune a clădirii inițiale.

## Ce se greșește în practică

- Se deduce integral, ca și cheltuială curentă, o investiție care de fapt majorează valoarea clădirii (de exemplu, o extindere sau o modernizare majoră a instalațiilor) — dacă investiția îndeplinește condiția de la lit. d), tratamentul corect e amortizarea, nu deducerea imediată.
- Se amortizează o simplă lucrare de întreținere (zugrăvit, reparație curentă) pe durata normală a clădirii, deși cheltuiala respectivă ar trebui dedusă integral, în anul efectuării — o confuzie care „întinde" nejustificat deducerea unei cheltuieli deja deductibile integral.
- Se folosește durata normală de funcționare a clădirii inițiale și pentru investiția ulterioară, fără să se verifice dacă investiția se amortizează pe durata rămasă a clădirii sau pe o durată proprie, stabilită separat.

## Ce face iConta.eu

Modulul de mijloace fixe din iConta.eu (`core/repo_mijloace_fixe.py`) permite introducerea unei investiții ca activ amortizabil separat, cu propria valoare, cont de imobilizare și durată normală de funcționare — mecanismul tehnic necesar pentru a trata corect o investiție într-o clădire existentă conform art. 28 alin. (3) lit. d). La data acestui ghid, aplicația **nu verifică automat** dacă o cheltuială introdusă îndeplinește condiția legală de „îmbunătățire a parametrilor tehnici și majorare a valorii" (deci dacă trebuie amortizată sau dedusă integral) — această calificare rămâne o evaluare profesională a contabilului, la introducerea documentului justificativ.

[iConta.eu](/)
