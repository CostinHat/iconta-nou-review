---
title: "Am calculat greșit deducerea personală"
description: "Majorările speciale ale deducerii personale — pentru angajații sub 26 de ani și pentru copilul înscris la școală — și condițiile lor obligatorii."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am calculat greșit deducerea personală

Pe lângă scara de bază (după numărul de persoane în întreținere), deducerea personală are două majorări speciale, fiecare cu propria condiție de eligibilitate. Omiterea condiției — nu doar a sumei — e sursa cea mai frecventă de eroare.

## Temeiul legal

::: ghid-temei
Codul fiscal, art.77 alin.(10) lit.a): majorare de **15% din salariul minim** pentru angajații **sub 26 de ani**, condiționată de venit sub pragul de la alin.(3) (salariul minim + 2.000 lei).

Codul fiscal, art.77 alin.(10) lit.b): majorare de **100 lei/lună** pentru fiecare copil **cu vârsta de până la 18 ani**, dacă acesta e înscris la învățământ, indiferent de nivelul venitului — dar condiționată, potrivit alin.(12)-(13), de existența unui document de înscriere și a unei declarații pe propria răspundere a părintelui (iar dacă părintele are mai mulți angajatori, și de o declarație de exclusivitate).
:::

Cele două majorări au logici diferite: cea pentru sub 26 de ani depinde de nivelul venitului (nu se acordă peste pragul legal), în timp ce cea pentru copilul cu vârsta de până la 18 ani înscris la școală nu depinde de venit, dar e strict condiționată de documente — nu se acordă niciodată "tacit", doar pe baza declarației verbale a angajatului.

## Ce se greșește în practică

Greșeli tipice: acordarea majorării de 15% pentru sub 26 de ani fără verificarea pragului de venit de la alin.(3), sau acordarea deducerii de 100 lei/copil fără documentul de înscriere și declarația pe propria răspundere prevăzute de alin.(12)-(13) — ori acordarea ei pentru un copil peste 18 ani, condiție pe care legea o cere explicit.

## Ce face iConta.eu

Motorul de calcul are un control explicit pentru deducerea de copil: dacă se introduce un număr de copii la școală fără ca declarația să fie bifată, calculul refuză să continue — nu acordă tacit deducerea. Această regulă implementează literal condiția din art.77 alin.(12)-(13).

Onest: pe acest punct există un semnal contradictoriu în sursele verificate. Codul de calcul conține un comentariu care marchează funcționalitatea drept "necablată" încă, iar un test intern din suita de teste încă înregistrează acest lucru ca o datorie tehnică deschisă. În același timp, fluxul real folosit la generarea statului de plată citește deja din baza de date datele necesare (data nașterii, numărul de copii școlarizați, declarația) și le transmite motorului de calcul. Nu s-a putut confirma dacă ecranul de introducere a acestor date există efectiv în interfață — așa că, dacă ai nevoie de această deducere, verifică direct în aplicație, la statul de plată al lunii, dacă poți introduce și salva aceste informații pentru salariatul respectiv.

[iConta.eu](/)
