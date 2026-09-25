---
title: "Cum se aplică TVA la cumpărarea unei mașini second-hand din UE?"
description: "TVA la o mașină second-hand cumpărată din UE depinde de trei factori: cine e vânzătorul, dacă a aplicat regimul de marjă, și dacă mașina e sau nu „mijloc de transport nou” în sensul Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se aplică TVA la cumpărarea unei mașini second-hand din UE?

„Mașină second-hand din UE" nu descrie o singură regulă de TVA, ci cel puțin trei situații legal diferite, cu tratamente diferite. Cine e vânzătorul (persoană fizică, dealer care aplică regimul de marjă, sau furnizor obișnuit) și dacă mașina se încadrează sau nu drept „mijloc de transport nou" în sensul Codului fiscal schimbă complet răspunsul.

## Temeiul legal

::: ghid-temei
„o achiziție intracomunitară de mijloace de transport noi, efectuată de orice persoană"
— Codul fiscal (Legea 227/2015), art. 268 alin. (3) lit. b) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- **Mijloc de transport nou** (definit de Codul fiscal după criterii de kilometraj/vechime, nu după cum arată colocvial) — achiziția lui intracomunitară e **întotdeauna** operațiune impozabilă în România, indiferent cine e cumpărătorul (persoană fizică sau juridică) și indiferent de calitatea vânzătorului. Regula e o excepție de la toate celelalte reguli de mai jos.
- Dacă mașina **nu** e mijloc de transport nou și e cumpărată de la o **persoană fizică** dintr-un alt stat membru (deci nu de la o persoană impozabilă care acționează ca atare), de regulă nu există TVA de plată la achiziție — nu se realizează o achiziție intracomunitară impozabilă în sensul art. 268 alin. (3) lit. a), pentru că lipsește o livrare intracomunitară taxabilă din partea vânzătorului.
- Dacă mașina e cumpărată de la un **dealer revânzător** care aplică, în statul lui, regimul special de marjă pentru bunuri second-hand — regimul reglementat de art. 312 Cod fiscal, aplicabil bunurilor mobile corporale refolosibile, achiziționate de revânzător în scopul revânzării — achiziția intră sub art. 312 alin. (2)/(11) lit. b), iar TVA se calculează pe marja profitului dealer-ului (preț de vânzare minus preț de cumpărare), nu pe prețul integral.
- Verificarea eligibilității reale a vânzătorului (dacă e chiar persoană impozabilă revânzătoare care a aplicat regimul de marjă în statul ei, dacă mașina e chiar „nouă" sau nu) e o judecată de fond, pe documentele tranzacției, nu un calcul automat.

## Ce se greșește în practică

- Se aplică regimul de marjă (art. 312) oricărei mașini cumpărate „second-hand" din UE, indiferent de vânzător — regimul se aplică doar dacă vânzătorul e o persoană impozabilă revânzătoare care l-a aplicat efectiv în statul ei; de la o persoană fizică sau de la un dealer obișnuit (fără regim de marjă), tratamentul e diferit.
- Se ignoră complet excepția mijloacelor de transport noi — dacă mașina se încadrează la această categorie, achiziția e taxabilă indiferent de calitatea vânzătorului, chiar dacă e cumpărată de la o persoană fizică.
- Se presupune că „second-hand" înseamnă automat „fără TVA de plată" — fals: în funcție de situație, TVA poate lipsi (persoană fizică, mașină nu e nouă), poate fi datorată pe marjă (dealer cu regim special) sau poate fi datorată integral (mijloc de transport nou, indiferent de vânzător).

## Ce face iConta.eu

Verificat direct în cod: motorul de TVA la marjă (`core/tva_marja.py`, funcționalitatea **F098 — Regim special marja (second-hand)**) calculează corect TVA-ul pe marja profitului — `marja = preț vânzare − preț cumpărare`, cu TVA prin procedeul sutei mărite — pentru situația în care regimul de marjă chiar se aplică, indiferent de proveniența bunului (formula primește doar prețul de achiziție, fără să facă distincție pe țara furnizorului). Ce **nu** face aplicația, verificat prin căutare directă în cod: nu clasifică o achiziție intracomunitară ca neimpozabilă atunci când vânzătorul e revânzător cu regim special (art. 268 alin. (8) lit. c)), nu verifică dacă vânzătorul e efectiv o „persoană impozabilă revânzătoare" în sensul legii, și nu distinge un „mijloc de transport nou" de unul second-hand — nu există în `core/` nicio funcționalitate de mijloace de transport noi. Decizia despre care dintre cele trei situații se aplică unei achiziții concrete rămâne, integral, o judecată a contabilului; aplicația calculează corect doar pasul final (TVA pe marjă), odată ce s-a stabilit că acest regim e cel aplicabil.

[iConta.eu](/)
