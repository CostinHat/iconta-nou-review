---
title: "Ce acte trebuie pentru radierea unei firme la Registrul Comerțului?"
description: "Actele obligatorii pentru cererea de radiere a unui SRL după lichidare, termenul legal de depunere și dovada fiscală cerută de Codul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce acte trebuie pentru radierea unei firme la Registrul Comerțului?

Radierea unei firme din registrul comerțului nu e un formular oarecare — e ultimul pas al unei proceduri de lichidare, iar legea condiționează explicit înregistrarea cererii de existența unor documente precise, printre care dovada plății impozitului datorat de asociați pentru câștigul din lichidare.

## Temeiul legal

::: ghid-temei
„În termen de 15 zile de la terminarea lichidării, lichidatorii vor depune la registrul comerțului cererea de radiere a societății din registrul comerțului, pe baza raportului final de lichidare și a situațiilor financiare de lichidare prin care se prezintă situația patrimoniului, a creanțelor și repartizarea activelor rămase, după caz, inclusiv, dacă este cazul, dovada îndeplinirii obligației de calculare, reținere și plată a impozitului pe venit din lichidarea societății, prevăzută la art. 97 alin. (5) din Legea nr. 227/2015 privind Codul fiscal [...], sub sancțiunea unei amenzi de 20 lei pe zi de întârziere [...]."
— Legea 31/1990, art. 260 alin. (6) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Deci actele obligatorii pentru cererea de radiere, potrivit textului legii, sunt:

- **raportul final de lichidare**, întocmit de lichidator;
- **situațiile financiare de lichidare**, care prezintă situația patrimoniului, a creanțelor și repartizarea activelor rămase între asociați;
- **dovada plății impozitului pe venitul din lichidare** (10%, impozit final, calculat, reținut și plătit de societate potrivit art. 97 alin. (5) Cod fiscal) — dar numai dacă operațiunea generează un asemenea venit impozabil la asociații persoane fizice (adică dacă rămân sume distribuite peste capitalul social vărsat);
- termenul de depunere a cererii: **15 zile de la terminarea lichidării**, sub sancțiunea unei amenzi de 20 lei/zi de întârziere, aplicată de registratorul de registrul comerțului.

## Ce se greșește în practică

- Se depune cererea de radiere fără dovada plății impozitului pe venitul din lichidare, deși există sume distribuite peste aporturi — cererea rămâne blocată sau se sancționează cu amenda de întârziere.
- Se confundă restituirea capitalului social vărsat (neimpozabilă la asociat) cu distribuirea rezervelor/profiturilor rămase (impozabilă cu 10%, impozit final) — impozitul se calculează greșit sau nu se calculează deloc.
- Se așteaptă ca termenul de 15 zile să curgă de la data hotărârii de dizolvare, nu de la **terminarea efectivă a lichidării** (adică după valorificarea activelor, stingerea datoriilor și întocmirea raportului final).

## Ce face iConta.eu

iConta.eu are un motor de calcul pentru lichidare (`core/lichidare.py`) care determină corect cota de 10%, impozit final, aplicabilă câștigului distribuit asociaților persoane fizice conform art. 97 alin. (5) din Codul fiscal, distinctă de regimul dividendelor. Aplicația nu depune însă cererea de radiere la Oficiul Registrului Comerțului și nu generează raportul final de lichidare sau situațiile financiare de lichidare — acestea rămân un pas manual al lichidatorului/contabilului, pe baza calculelor produse de aplicație.

[iConta.eu](/)
