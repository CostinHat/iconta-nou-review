---
title: "Cum reconciliez contul 4411 cu fișa ANAF?"
description: "Ce reprezintă contabil soldul contului 4411 și cum se compară cu evidența oficială a obligațiilor fiscale ținută de organul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum reconciliez contul 4411 cu fișa ANAF?

Contul 441 „Impozitul pe profit și alte impozite" (cu analiticul 4411 pentru impozitul pe profit) trebuie să reflecte, la orice moment, aceeași realitate pe care o are și organul fiscal despre firma ta: cât ai declarat, cât ai plătit și ce sold a rămas. Diferențele dintre soldul din contabilitate și „fișa" ținută de ANAF apar frecvent din decalaje de înregistrare, nu din erori de calcul propriu-zise.

## Temeiul legal

::: ghid-temei
„(1) În scopul exercitării activității de colectare a creanțelor fiscale, organul fiscal organizează, pentru fiecare contribuabil/plătitor, evidența creanțelor fiscale și modul de stingere a acestora. Evidența se organizează pe baza titlurilor de creanță fiscală și a actelor referitoare la stingerea creanțelor fiscale. (2) Contribuabilul/Plătitorul are acces la informațiile din evidența creanțelor fiscale, la cererea acestuia, adresată organului fiscal competent."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 153 alin. (1)-(2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce spune legea, tradus pentru reconciliere:

- Ceea ce colocvial se numește „fișa pe plătitor" sau „fișa ANAF" e, legal, evidența creanțelor fiscale organizată de organul fiscal pentru fiecare contribuabil, pe baza titlurilor de creanță (declarațiile depuse) și a actelor de stingere (plăți, compensări). Ai dreptul de acces la ea, la cerere sau prin spațiul privat virtual.
- În contabilitate, contul 441 se creditează cu impozitul pe profit/impozitul pe veniturile microîntreprinderilor datorat (calculat prin 691/698 = 441) și se debitează cu sumele efectiv virate către buget (441 = 512), conform funcțiunii stabilite prin reglementările contabile.
- O reconciliere corectă compară **soldul creditor** al contului 4411 din balanța de verificare cu **soldul debitor rămas de plată** din fișa ANAF, la aceeași dată de referință — cele două trebuie să coincidă dacă toate declarațiile depuse au fost înregistrate corect în contabilitate și toate plățile confirmate de bancă au fost operate.

## Ce se greșește în practică

- Se compară soldurile la date diferite (de exemplu soldul contabil de la sfârșitul lunii cu fișa ANAF extrasă câteva zile mai târziu, care deja include o plată nouă), ceea ce produce diferențe aparente.
- Se omite înregistrarea unei decizii de impunere emise de ANAF (de exemplu în urma unui control) direct în 4411, deși fișa ANAF o reflectă deja ca obligație.
- Se ignoră dobânzile și penalitățile de întârziere calculate de ANAF pe alt cont (nu 4411, ci conturi de datorii accesorii), ceea ce face ca diferența dintre solduri să pară o eroare de bază, când de fapt ține de accesorii fiscale, nu de impozitul propriu-zis.
- Se presupune că declarația depusă = automat plata înregistrată corect, fără verificarea efectivă a datei de valută și a sumei confirmate de bancă/Trezorerie.

## Ce face iConta.eu

iConta.eu are un modul de control încrucișat și audit al preluării datelor care mapează explicit contul 4411 la declarația de impozit pe profit (D101) și urmărește coerența dintre soldurile fiscale din contabilitate și istoricul declarațiilor depuse. Reconcilierea „asociați/cote, mijloace fixe, salariați, vector fiscal vs. documente" e marcată în aplicație ca strat neimplementat în prima versiune a acestui control, dar maparea de bază 4411 ↔ D101 (impozit pe profit) există și funcționează ca punct de plecare pentru verificare.

[iConta.eu](/)
