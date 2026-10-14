---
title: "Cum corectez o bază de impozitare a dividendelor declarată greșit"
description: "De unde provine baza de impozitare a dividendelor în D205 și cum se corectează atunci când este greșită."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum corectez o bază de impozitare a dividendelor declarată greșit

Baza de impozitare (`baza1`) raportată în D205 pentru un beneficiar de dividende nu este o valoare introdusă direct — ea rezultă din suma efectiv plătită acelui asociat, citită din contabilitate. O bază greșită are, de regulă, o cauză la sursă.

## Temeiul legal

::: ghid-temei
„Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor/sumelor reprezentând câștigul obținut ca urmare a deținerii de titluri de participare de către acționari/ asociați/investitori.”
— Codul fiscal (Legea 227/2015), art. 97 alin. (7) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))

„Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă.”
— Codul de procedură fiscală (Legea 207/2015), art. 105 alin. (2) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))

„Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative.”
— Codul de procedură fiscală (Legea 207/2015), art. 105 alin. (3) (sursă: [Legea nr. 207/2015 privind Codul de procedură fiscală](https://legislatie.just.ro/Public/DetaliiDocument/170007))
:::

## Ce se greșește în practică

Se corectează uneori direct suma din ecranul declarației, fără a verifica nota contabilă de pe contul 457 din care a fost preluată baza — corecția "dispare" la următoarea regenerare, pentru că sursa contabilă rămâne neschimbată.

## Ce face iConta.eu

Deoarece baza de impozitare este calculată din dividendul efectiv **plătit** (debitul contului 457), o bază greșită înseamnă aproape întotdeauna o sumă greșită înregistrată pe acea notă contabilă, sau o cotă aplicată de la o dată greșită de distribuire (algoritmul FIFO din aplicație potrivește tranșele de plată cu distribuirile corespunzătoare). Pentru beneficiarii preluați automat din contul 457, mecanismul de reconciliere recalculează independent baza și impozitul și blochează generarea la orice divergență — deci corectarea trebuie făcută la nivelul notei contabile pe 457, nu în declarație. Pentru beneficiarii introduși manual, reconcilierea completă nu se aplică; se verifică doar intern că impozitul introdus corespunde formulei cotă × bază, astfel încât corectitudinea bazei rămâne în răspunderea celui care a introdus-o. Dacă declarația cu baza greșită a fost deja depusă la ANAF, rețineți că iConta nu generează în prezent o D205 rectificativă (vezi ghidul dedicat acestui subiect).

[iConta.eu](/)
