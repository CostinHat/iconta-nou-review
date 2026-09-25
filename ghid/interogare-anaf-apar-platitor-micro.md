---
title: "Interogare ANAF: apar ca plătitor de micro"
description: "De ce o firmă poate apărea în evidențele ANAF ca plătitoare de impozit pe veniturile microîntreprinderilor, deși nu a depus explicit o opțiune în acest sens."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Interogare ANAF: apar ca plătitor de micro

Nu e o eroare de sistem, de cele mai multe ori — e mecanismul legal de încadrare. Regimul de microîntreprindere e opțional, dar aplicarea lui, odată îndeplinite condițiile, nu cere o cerere separată de „intrare"; cere, dimpotrivă, o comunicare explicită dacă firma vrea să iasă din el.

## Temeiul legal

::: ghid-temei
„Articolul 48 Reguli de aplicare a sistemului de impunere pe veniturile microîntreprinderii
(1) Impozitul reglementat de prezentul titlu este opțional.
(2) Persoanele juridice române pot opta să aplice impozitul reglementat de prezentul titlu începând cu anul fiscal următor celui în care îndeplinesc condițiile de microîntreprindere prevăzute la art. 47 alin. (1).
[...]
(3) O persoană juridică română care este nou-înființată poate opta să plătească impozit pe veniturile microîntreprinderilor începând cu primul an fiscal, dacă condițiile prevăzute la art. 47 alin. (1) lit. d) și h) sunt îndeplinite la data înregistrării în registrul comerțului, iar cea prevăzută la lit. g) în termen de 90 de zile inclusiv de la data înregistrării persoanei juridice respective."
— Legea 227/2015 (Codul fiscal), art. 48 alin. (1)-(3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce explică asta pentru rezultatul interogării ANAF:

- **„Opțional" nu înseamnă că firma trebuie să ceară explicit** aplicarea regimului micro în fiecare an — pentru o firmă nou-înființată, opțiunea se exercită o singură dată, la înregistrare (alin. 3), dacă îndeplinește condițiile de capital (art. 47 alin. 1 lit. d), structura asociaților (lit. h) — asociați/acționari care dețin peste 25% și unicitatea microîntreprinderii desemnate și, în 90 de zile, condiția de angajat (lit. g).
- **Pentru firmele existente**, dacă la 31 decembrie anul precedent îndeplinesc condițiile de la art. 47 alin. (1) — inclusiv plafonul de venituri, capitalul deținut de persoane private, lipsa dizolvării — ele rămân/devin plătitoare de impozit pe veniturile microîntreprinderilor pentru anul următor, fără să fie nevoie de o cerere repetată de confirmare.
- **A ieși din regim** cere o comunicare explicită către organul fiscal — declarație de mențiuni prin care se optează pentru impozit pe profit. Art. 55 (Termenele de declarare a mențiunilor) stabilește aceste termene: aplicarea regimului se comunică până la 31 martie a anului pentru care se plătește impozitul (alin. 2), iar ieșirea din regim, atunci când o condiție de la art. 47 alin. (1) nu mai e îndeplinită, se comunică tot până la 31 martie a anului fiscal următor (alin. 3). Fără această comunicare, firma continuă să apară ca „plătitor de micro" în evidențele ANAF.
- Interogarea publică ANAF (vectorul fiscal al firmei) reflectă exact ultima situație comunicată/înregistrată — dacă firma nu a depus nicio declarație de opțiune pentru profit, iar condițiile de la art. 47 sunt îndeplinite, „micro" e rezultatul corect al aplicării legii, nu o eroare de încadrare.

## Ce se greșește în practică

- Se presupune că regimul fiscal se schimbă automat dacă firma nu mai îndeplinește condițiile „din interior" (de exemplu, plafonul de venituri e depășit în cursul anului) — corect e că unele situații (depășirea plafonului de 100.000 euro) chiar declanșează trecerea automată la profit în cursul anului (art. 52), dar alte condiții (capitalul social, sediul) nu se verifică automat de sistem fără o comunicare.
- Se ignoră termenul de comunicare a ieșirii din regimul micro (declarație de mențiuni), presupunând că simpla depunere a unei declarații de impozit pe profit e suficientă — organul fiscal urmărește comunicarea explicită a schimbării de regim.
- Se confundă „microîntreprindere" (regim de impozit pe venit, Titlul III din Codul fiscal) cu „micro-entitate" (categorie de mărime pentru situațiile financiare, conform OMFP 1802/2014) — sunt clasificări diferite, cu criterii și efecte diferite; una nu implică automat pe cealaltă.

## Ce face iConta.eu

Vectorul fiscal din iConta.eu (`core/vector_fiscal_api.py`) tratează distinct regimul fiscal (micro sau profit) pentru firmele cu contabilitate în partidă dublă (SRL) — regim pe care contabilul îl setează explicit la nivel de firmă, separat de categoria de mărime contabilă (micro-entitate/entitate mică, folosită pentru simplificarea situațiilor financiare, calculată în `core/categorie_marime.py` pe baza pragurilor din OMFP 1802/2014). Aplicația nu interoghează automat ANAF pentru a confirma regimul fiscal real al firmei — contabilul verifică direct pe portalul ANAF ce regim apare înregistrat și configurează corespunzător firma în iConta.eu.

[iConta.eu](/)
