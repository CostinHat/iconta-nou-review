---
title: "Marfa expirată este cheltuială deductibilă?"
description: "Regimul fiscal, la impozitul pe profit, al pierderilor din marfă cu termen de valabilitate depășit — deductibilitate limitată, nu integrală."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Marfa expirată este cheltuială deductibilă?

Marfa care expiră pe raft sau în depozit e o realitate a oricărui comerciant, dar Codul fiscal nu o tratează ca pe o cheltuială oricare. Casarea unor bunuri cu termen de valabilitate depășit intră într-o categorie specială — cea a scăzămintelor și perisabilităților — cu **deductibilitate limitată**, nu deductibilitate integrală și necondiționată.

## Temeiul legal

::: ghid-temei
„Pentru determinarea rezultatului fiscal sunt considerate cheltuieli deductibile cheltuielile efectuate în scopul desfășurării activității economice [...]." [alin. (1)] „Următoarele cheltuieli au deductibilitate limitată: [...] d) scăzămintele, perisabilitățile, pierderile rezultate din manipulare/depozitare, potrivit legii [...]."
— Codul fiscal (Legea 227/2015), art. 25 alin. (1) și alin. (3) lit. d) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Regula generală de la alin. (1) — cheltuiala e deductibilă dacă e făcută „în scopul desfășurării activității economice" — nu se aplică fără rezerve pierderilor din marfă expirată: art. 25 alin. (3) lit. d) le încadrează explicit la **cheltuieli cu deductibilitate limitată**.
- Limita nu e o sumă fixă stabilită de Codul fiscal, ci trimite la „potrivit legii" — adică la normele legale de perisabilități aplicabile categoriei de bunuri (limite de scădere din gestiune, stabilite prin acte normative distincte pentru fiecare tip de marfă). Ce depășește norma legală de perisabilitate **nu este deductibil**.
- Codul fiscal distinge pierderea din perisabilitate obișnuită (evaporare, scădere naturală) de pierderea din bunuri cu termen de valabilitate expirat, dar le pune sub aceeași literă d) și sub același regim de deductibilitate limitată.
- Simpla casare a mărfii expirate, fără documentele justificative (proces-verbal de casare, dovada scoaterii din gestiune, încadrarea în norma legală), nu susține deductibilitatea în fața unui control.

## Ce se greșește în practică

- Se consideră automat că orice marfă expirată casată e 100% deductibilă, ca orice altă cheltuială „legată de activitate" — de fapt e supusă limitei din art. 25 alin. (3) lit. d).
- Nu se întocmește procesul-verbal de casare sau nu se păstrează dovada scoaterii fizice din gestiune, ceea ce lasă cheltuiala fără suport documentar în caz de inspecție.
- Se confundă deductibilitatea la impozitul pe profit cu tratamentul la TVA — casarea mărfii expirate poate ridica și obligații de ajustare a TVA deduse inițial, o problemă separată de deductibilitatea cheltuielii.
- Se aplică aceeași logică nediferențiat, indiferent de tipul de marfă, deși normele de perisabilitate diferă în funcție de natura bunurilor.

## Ce face iConta.eu

La verificarea codului sursă, iConta.eu are un modul dedicat (`perisabilitati.py`, construit pe HG 831/2004 și art. 25/art. 304 din Codul fiscal) care calculează limita deductibilă (valoarea intrărilor × procentul-limită), separă partea deductibilă de cea nedeductibilă și determină automat ajustarea de TVA aferentă depășirii (potrivit art. 304 CF), cu excepția expresă a cazului de degradare calitativă dovedită prin distrugere. Modulul **nu deduce însă singur procentul-limită** din anexele HG 831/2004 pentru fiecare categorie de produs — acesta trebuie furnizat ca parametru (`procent_limita`), pe baza încadrării făcute de contabil în funcție de natura mărfii.

[iConta.eu](/)
