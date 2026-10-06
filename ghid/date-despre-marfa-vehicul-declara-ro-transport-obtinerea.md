---
title: "Ce date despre marfă și vehicul se declară în RO e-Transport pentru obținerea codului UIT?"
description: "Se declară expeditorul și beneficiarul, denumirea, caracteristicile, cantitățile și valoarea bunurilor, locurile de încărcare și descărcare și datele mijlocului de transport."
published: 2026-09-29
modified: 2026-09-29
poarta: v1
---

# Ce date despre marfă și vehicul se declară în RO e-Transport pentru obținerea codului UIT?

OUG 41/2022 stabilește conținutul declarației prin modulele informatice ale sistemului. Se înregistrează **părțile** (expeditor și beneficiar), **marfa** (denumire, caracteristici, cantitate, contravaloare), **traseul** (locul de încărcare și locul de descărcare) și **mijlocul de transport**. Pe baza acestor date sistemul generează codul UIT.

Datele trebuie să corespundă transportului real. Declararea unor cantități diferite de cele transportate este contravenție distinctă, sancționată pentru persoanele juridice cu amendă de la 20.000 la 100.000 de lei și cu confiscarea contravalorii bunurilor nedeclarate.

## Temeiul legal

::: ghid-temei
„(1) Sistemul RO e-Transport include: a) module informatice de gestiune a transporturilor de bunuri prin care sunt înregistrate datele referitoare la expeditor și beneficiar, denumirea, caracteristicile, cantitățile și contravaloarea bunurilor transportate, locurile de încărcare și descărcare, detalii cu privire la mijlocul de transport utilizat, precum și codul UIT generat;"
— OUG 41/2022, art. 4 alin. (1) lit. a) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))

„b) declararea în Sistemul RO e-Transport a unor cantități diferite de cele care fac obiectul transportului de bunuri;"
— OUG 41/2022, art. 13^1 alin. (1) lit. b) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))

„(2) Contravențiile prevăzute la alin. (1) lit. a) și b) se sancționează cu amendă de la 10.000 de lei la 50.000 de lei în cazul persoanelor fizice sau cu amendă de la 20.000 de lei la 100.000 de lei în cazul persoanelor juridice, precum și confiscarea contravalorii bunurilor nedeclarate."
— OUG 41/2022, art. 13^1 alin. (2) (sursă: [OUG nr. 41/2022 pentru instituirea Sistemului național RO e-Transport](https://legislatie.just.ro/Public/DetaliiDocument/253801))
:::

Pe grupe, datele care se declară:

- **Părțile**: expeditorul și beneficiarul, adică partenerul comercial, cu țara și codul de identificare.
- **Bunurile**: denumirea, caracteristicile (în practică, codul tarifar NC al fiecărui produs), cantitatea cu unitatea de măsură și contravaloarea. Formularul oficial cere și greutatea netă și brută, precum și scopul operațiunii.
- **Traseul**: locul de încărcare și locul de descărcare, cu adresa.
- **Mijlocul de transport**: numărul de înmatriculare al vehiculului și, după caz, al remorcii, precum și transportatorul.
- **Data transportului**: data declarată pentru începerea transportului. De la ea curge valabilitatea codului UIT: 5 zile, respectiv 15 zile în cazurile prevăzute de art. 11 alin. (2).

Se declară **toate** bunurile din partidă, dacă în ea sunt amestecate bunuri cu risc fiscal ridicat și alte bunuri (art. 12 alin. (1)).

::: ghid-exemplu
SC Exemplu SRL vinde în țară 20 t de bare de oțel (NC 7214) cu 90.000 lei fără TVA. În RO e-Transport declară:

- partener: SC Client SRL, cu CUI-ul;
- bun: bare de oțel, cod NC 7214, 20.000 kg, greutate netă 20.000 kg, greutate brută 20.150 kg, valoare 90.000 lei;
- traseu: depozitul din Ploiești → șantierul clientului din Brașov;
- vehicul: numărul camionului și al remorcii, transportatorul;
- data transportului: ziua plecării.

Dacă în camion se încarcă de fapt 22 t, declarația nu corespunde transportului real, iar faptul poate fi sancționat conform art. 13^1.
:::

## Ce se greșește în practică

- **Se declară cantitatea din comandă, nu din încărcare.** Cantitatea trebuie să fie cea transportată efectiv.
- **Codul NC e aproximat.** De el depinde încadrarea ca bun cu risc fiscal ridicat.
- **Se omit bunurile din afara listei dintr-o partidă mixtă.** Art. 12 cere declararea lor.
- **Se corectează datele după plecare.** Datele nu se mai pot modifica după punerea în mișcare a vehiculului (art. 11 alin. (3)). Singura excepție este actualizarea vehiculului (art. 8 alin. (1^1)).

## Ce face iConta.eu

Cardul e-Transport din iConta.eu are câmpuri pentru toate aceste grupe de date: tipul operațiunii, bunurile (scop, cod tarifar, denumire, cantitate, UM, greutate netă și brută, valoare fără TVA), partenerul, vehiculul și transportatorul, locurile de pornire și de sosire. XML-ul notificării (structura oficială v2) se generează doar când câmpurile obligatorii sunt completate. Câmpurile lipsă sunt semnalate unul câte unul. Corectitudinea cantităților față de încărcarea reală rămâne în sarcina firmei.

[iConta.eu](/)
