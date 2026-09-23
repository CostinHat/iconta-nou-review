---
title: D205 pentru dividende încasate de un salariat
description: Un asociat care e și angajat al societății încasează dividendul sub un regim complet separat de salariu — cotă diferită, mecanism diferit, fără nicio legătură între cele două.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D205 pentru dividende încasate de un salariat

E frecvent ca un asociat al unei societăți mici sau mijlocii să fie, în același timp, și angajat al acesteia (de exemplu administrator cu contract de muncă sau salariat pe altă poziție). Cele două venituri — salariul și dividendul — au regimuri fiscale total diferite și nu se amestecă: salariul e supus impozitului pe venit și contribuțiilor sociale (CAS, CASS) prin mecanismul de salarizare, iar dividendul e impozitat separat, cu 16% (sau cota istorică aplicabilă), reținut la sursă de societate și declarat prin D205.

## Temeiul legal

::: ghid-temei
"(7) Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câștigul obținut ca urmare a deținerii de titluri de participare de către acționari/asociați/investitori."
— Codul fiscal, Legea 227/2015, art. 97 alin. (7)
:::

Regimul descris de acest text privește strict calitatea de acționar/asociat/investitor și nu face nicio referire la eventuala calitate de salariat a beneficiarului. Faptul că persoana respectivă are și un contract de muncă cu societatea nu schimbă cota, mecanismul de reținere sau termenele aplicabile dividendului.

## Ce se greșește în practică

- Se raportează dividendul încasat de un asociat-salariat prin statul de plată sau declarația specifică salariilor (D112) — dividendul nu e venit salarial și nu trece prin acel circuit; el se declară exclusiv prin D205.
- Se presupune că impozitul deja reținut pe salariu "acoperă" și dividendul, sau invers — sunt două calcule complet independente, pe baze de impozitare diferite, cu cote diferite.
- Se confundă, la generarea D205, calitatea de salariat cu cea de asociat — D205 privește exclusiv fluxul de dividende (contul 457) și cotele de participare, nu contractul de muncă al beneficiarului.

## Ce face iConta.eu

Motorul D205 din iConta.eu identifică beneficiarii exclusiv din lista de asociați/acționari cu cotă de participare peste 0% și din mișcările contului 457 — nu interoghează și nu ține cont de statutul de angajat al beneficiarului respectiv (salariile se gestionează într-o funcționalitate separată, complet independentă de F029). Pentru un asociat care e și salariat, D205 tratează partea de dividend exact ca la orice alt beneficiar: bază calculată pe dividendul plătit, cotă valabilă la data distribuirii, impozit final reținut de societate.

[iConta.eu](/)
