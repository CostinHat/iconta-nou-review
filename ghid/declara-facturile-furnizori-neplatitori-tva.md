---
title: "Se declară facturile de la furnizori neplătitori de TVA în D394?"
description: "Cine intră în declarația 394 ca partener de achiziție atunci când furnizorul nu are cod de TVA, și ce spune ordinul ANAF despre asta."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Se declară facturile de la furnizori neplătitori de TVA în D394?

D394 nu se limitează la operațiunile cu alți plătitori de TVA. Obligația de declarare ține de faptul că firma ta e înregistrată în scopuri de TVA, nu de statutul fiscal al partenerului — așa că, în principiu, și achizițiile de la un furnizor neplătitor de TVA pot ajunge în declarație, cu o mențiune importantă despre ce anume se exclude.

## Temeiul legal

::: ghid-temei
„Persoanele impozabile înregistrate în scopuri de TVA în România sunt obligate să declare livrările de bunuri, prestările de servicii şi achiziţiile de bunuri şi servicii realizate pe teritoriul României către/de la orice persoană, aşa cum este definită la art. 266 alin. (1) pct. 24 din Legea nr. 227/2015 privind Codul fiscal, cu modificările şi completările ulterioare."
— OPANAF 3769/2015, art.1 (sursă: anaf_surse/opanaf_3769_2015_d394_baza.txt:20-24)

„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025, Anexa 2 pct.1 lit.b) (sursă: anaf_surse/opanaf_2194_2025_d394.txt:741-742)
:::

Din cele două texte rezultă regula practică:

- Obligația de declarare în D394 e legată de faptul că **tu** ești înregistrat în scopuri de TVA — nu există niciun prag și nu contează dacă furnizorul concret e sau nu plătitor de TVA.
- Textul de lege exclude explicit un singur tip de achiziție din D394: **achizițiile intracomunitare**, care se declară în D390 (VIES). Achizițiile de la un furnizor din România, chiar dacă acesta nu e înregistrat în scopuri de TVA, nu intră în această excludere — rămân, ca principiu, achiziții taxabile efectuate pe teritoriul României, de tipul celor pe care Anexa 2 le cere declarate.
- Distincția „plătitor de TVA" vs. „neplătitor de TVA" al furnizorului nu schimbă obligația de declarare a operațiunii — schimbă doar modul de clasificare a partenerului în structura formularului.

## Ce se greșește în practică

- Se presupune, din reflex, că „neplătitor de TVA" înseamnă automat „nu intră în D394" — regula de excludere din lege vizează exclusiv achizițiile **intracomunitare**, nu pe cele de la un furnizor autohton fără cod de TVA.
- Se confundă furnizorul neplătitor de TVA cu furnizorul din alt stat membru — sunt două situații diferite, cu tratament diferit (declarația 390 vs. 394).
- Se ignoră faptul că firma proprie trebuie să fie plătitoare de TVA pentru a avea, în general, obligația D394 — dacă firma ta nu e înregistrată în scopuri de TVA, nu depui D394 indiferent de statutul furnizorilor.

## Ce face iConta.eu

Generatorul D394 din iConta.eu clasifică fiecare partener din factură după prefixul CUI, în cod (`core/d394.py`, funcția `clasifica_partener()`): plătitor RO cu prefix valid, partener fără cod de TVA, partener din UE și partener din afara UE. Aplicația nu tratează tacit un partener autohton fără cod de TVA ca fiind „în afara declarației" — clasificarea există tocmai ca să deosebească acest caz de un partener străin.

Ce nu face aplicația: nu verifică independent, la generare, dacă un CUI RO scris fără prefix e efectiv un CUI valid de neplătitor de TVA sau o simplă greșeală de tastare a codului „RO" — există totuși un gard care semnalează un CUI RO scris greșit înainte ca acesta să fie declarat tacit drept partener străin. Achizițiile intracomunitare sunt excluse explicit din generare (comentariu în cod: „ACHIZITIILE INTRACOMUNITARE NU INTRA IN D394 - se declara in D390"), în timp ce achizițiile de la furnizori autohtoni, indiferent de statutul lor de TVA, urmează fluxul normal de generare.

[iConta.eu](/)
