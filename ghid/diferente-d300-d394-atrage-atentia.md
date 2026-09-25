---
title: "Ce diferențe între D300 și D394 pot atrage atenția ANAF?"
description: "D300 și D394 nu declară aceleași sume — D300 conține tot TVA-ul firmei, D394 doar subsetul național raportabil. Ce diferențe sunt normale și ce merită verificat."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce diferențe între D300 și D394 pot atrage atenția ANAF?

D300 (decontul de TVA) și D394 nu ar trebui comparate cifră cu cifră, ca și cum ar trebui să fie identice — relația dintre ele e de **incluziune**, nu de egalitate. D300 conține tot TVA-ul firmei, inclusiv operațiunile intracomunitare și importurile; D394 conține doar subsetul de operațiuni naționale raportabile conform propriei sale sfere.

## Temeiul legal

::: ghid-temei
„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025 (care modifică Anexa 2 a OPANAF 3769/2015), aplicabil operațiunilor derulate de la 1.08.2025 (sursă: anaf_surse/opanaf_2194_2025_d394.txt)
:::

Din text și din structura celor două formulare rezultă exact ce nu trebuie să coincidă:

- **achizițiile intracomunitare** sunt excluse explicit din D394 — ele se raportează în D390 (VIES), nu în D394, deși apar în decontul de TVA (D300);
- **livrările intracomunitare**, în schimb, **nu** sunt excluse din D394 — apar acolo la fel ca exporturile, ca operațiune scutită la cotă 0 (tip LS), deși sunt raportate simultan și în D390;
- o discrepanță reală de urmărit e alta decât „D300 ≠ D394": e situația în care D300 conține TVA colectat/dedus pentru operațiuni naționale care lipsesc complet din D394, fără nicio explicație structurală (import, operațiune intracomunitară, sau altă excludere legală).

## Ce se greșește în practică

- Se așteaptă ca totalul bazei impozabile din D300 să fie identic cu totalul din D394 — structural, D300 e mai mare, pentru că include și operațiunile intracomunitare/importurile pe care D394 le exclude explicit.
- Se omite verificarea inversă — o operațiune națională taxabilă care apare în D300, dar lipsește din D394 fără motiv legal (nu e intracomunitară, nu e o excludere cunoscută), e exact tipul de diferență care poate atrage atenția organului fiscal la o verificare încrucișată.
- Se ignoră tratamentul livrărilor scutite către parteneri cu CUI românesc valid — acestea trebuie incluse în D394 ca tip LS (cotă 0), indiferent de tipul partenerului, nu omise pentru că au cotă zero.

## Ce face iConta.eu

Generatorul D394 exclude explicit din calcul achizițiile intracomunitare (direcția „primită" de la parteneri UE/non-UE), cu comentariu direct în cod care citează exact motivul: acestea se declară în D390, nu în D394. Relația de incluziune D300⊇D394 e documentată explicit și în motorul de reconciliere al aplicației.

Pe lângă excluderea corectă a achizițiilor intracomunitare, aplicația rulează o **a doua cale de calcul, independentă**: recalculează totalurile pe cotă de TVA direct din liniile brute ale facturilor, separat de generatorul principal, și **blochează** generarea declarației dacă cele două căi diferă — numind explicit valorile și câmpul divergent. Limitele declarate ale acestui gard: nu acoperă operațiunile manuale (bonuri/borderouri, fără ecran propriu la data acestui ghid) și nu prinde o eroare de intrare comună ambelor căi de calcul (de exemplu o cotă de TVA tastată greșit o singură dată, direct pe factură).

[iConta.eu](/)
