---
title: D205 pentru dividende după modificare de capital
description: D205 nu ține cont, prin ea însăși, de o eventuală majorare sau reducere anterioară de capital social — citește doar contul 457 și cotele de participare actuale ale asociaților. Ce trebuie verificat manual în acest caz.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D205 pentru dividende după modificare de capital

Dacă societatea a trecut printr-o modificare de capital social (majorare sau reducere, cu sau fără schimbarea structurii asociaților) înainte de o distribuire de dividende, D205 în sine nu tratează separat acest context — declarația nu "știe" de o modificare de capital, ci citește exclusiv soldurile contului 457 și cotele de participare ale asociaților/acționarilor așa cum sunt înregistrate la momentul generării. Tocmai de aceea, corectitudinea declarației depinde direct de actualizarea cotelor în evidența contabilă.

## Temeiul legal

::: ghid-temei
"(7) Veniturile sub formă de dividende, inclusiv câștigul obținut ca urmare a deținerii de titluri de participare definite de legislația în materie la organisme de plasament colectiv, se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final."
— Codul fiscal, Legea 227/2015, art. 97 alin. (7)
:::

Cota de impozitare a dividendelor (art. 97 alin. (7) de mai sus) se aplică sumei distribuite/plătite, indiferent de operațiunile anterioare de capital social. Cercetarea care stă la baza acestui ghid nu a identificat, nici în structura oficială a D205, nici în instrucțiunile ei de completare, nici în codul funcționalității F029, vreo regulă specifică legată de o modificare anterioară a capitalului social — nu există, la acest nivel, un temei separat de cel general (art. 97 alin. (7)), iar acest ghid nu inventează unul.

## Ce se greșește în practică

- Se presupune, greșit, că o majorare sau reducere de capital social schimbă, prin ea însăși, regimul fiscal al unei distribuiri ulterioare de dividende — nu e cazul; regimul rămâne cel obișnuit (art. 97 alin. (7)).
- Cea mai frecventă greșeală reală: după o modificare de capital care schimbă structura asociaților (intrare/ieșire de asociați, redistribuire de cote), cotele de participare din evidența contabilă nu sunt actualizate la zi — iar o distribuire ulterioară de dividende se împarte automat pe cotele **vechi**, nu pe cele rezultate din modificare.
- Se generează D205 imediat după modificarea de capital, fără a verifica întâi dacă hotărârea de majorare/reducere a fost deja reflectată corect în cotele asociaților din aplicație.

## Ce face iConta.eu

Generatorul D205 din iConta.eu împarte automat dividendul distribuit/plătit pe asociați/acționari strict după cotele de participare înregistrate la momentul generării (`select_asociati`, doar cei cu cotă peste 0%) și după mișcările contului 457 din note validate — nu păstrează, pentru F029, un istoric al modificărilor de capital social și nu ajustează singur cotele în urma unei asemenea modificări. Dacă societatea dumneavoastră a trecut printr-o modificare de capital care schimbă structura de asociați sau procentele deținute, actualizați întâi cotele asociaților în iConta.eu, înainte de a genera D205 pentru o distribuire ulterioară — altfel riscați o împărțire a impozitului pe cote care nu mai reflectă structura reală.

[iConta.eu](/)
