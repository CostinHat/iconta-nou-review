---
title: Cum se înregistrează contabil concediile medicale?
description: Indemnizația de concediu medical se înregistrează prin contul 423 — partea suportată de angajator pe cheltuieli (6458 = 423), partea din FNUASS ca sumă de recuperat (4382 = 423), iar contribuțiile și impozitul reținute din indemnizație din 423. iConta.eu le include în nota statului de plată.
published: 2026-09-24
modified: 2026-10-13
poarta: v1
---

# Cum se înregistrează contabil concediile medicale?

Indemnizațiile de concediu medical sunt reglementate separat de salariu, prin OUG 158/2005, și au contul lor: 423 „Personal - ajutoare materiale datorate”. Primele zile de incapacitate le suportă angajatorul, restul se suportă din bugetul Fondului național unic de asigurări sociale de sănătate (FNUASS) și se recuperează de acolo.

## Temeiul legal

::: ghid-temei
„Indemnizațiile pentru incapacitate temporară de muncă se suportă după cum urmează: A. de către angajator, din prima zi până în a 5-a zi de incapacitate temporară de muncă, [...] B. din bugetul Fondului național unic de asigurări sociale de sănătate, începând cu: a) ziua următoare celor suportate de angajator, conform lit. A , și până la data încetării incapacității temporare de muncă a asiguratului sau a pensionării acestuia;”
— OUG 158/2005, art. 12 (sursă: [OUG nr. 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate](https://legislatie.just.ro/Public/DetaliiDocument/66305))

„(1) Sumele reprezentând indemnizații, care se plătesc asiguraților și care, potrivit prevederilor prezentei ordonanțe de urgență, se suportă din bugetul Fondului național unic de asigurări sociale de sănătate, se recuperează din bugetul Fondului național unic de asigurări sociale de sănătate din creditele bugetare prevăzute cu această destinație. Aceste sume nu pot fi recuperate din sumele constituite reprezentând contribuție de asigurări sociale de sănătate.”
— OUG 158/2005, art. 38 alin. (1) (sursă: [OUG nr. 158/2005 privind concediile și indemnizațiile de asigurări sociale de sănătate](https://legislatie.just.ro/Public/DetaliiDocument/66305))

„Contul 423 "Personal - ajutoare materiale datorate" Cu ajutorul acestui cont se ține evidența ajutoarelor de boală pentru incapacitate temporară de muncă, a celor pentru îngrijirea copilului, a ajutoarelor de deces și a altor ajutoare acordate. [...] În creditul contului 423 "Personal - ajutoare materiale datorate" se înregistrează: – ajutoarele materiale suportate potrivit legii, precum și alte ajutoare acordate (431, 645). ... În debitul contului 423 "Personal - ajutoare materiale datorate" se înregistrează: – ajutoare materiale achitate (512, 531); ... – reținerile reprezentând avansuri acordate, sume datorate unității sau terților, contribuția pentru asigurări sociale, contribuția pentru asigurări de sănătate și pentru ajutorul de șomaj și impozitul datorat (425, 427, 428, 431, 437, 444);”
— OMFP 1802/2014, anexa nr. 1, contul 423 (sursă: [OMFP nr. 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate)](https://legislatie.just.ro/Public/DetaliiDocument/164320))

„În debitul contului 645 "Cheltuieli privind asigurările și protecția socială" se înregistrează: – sumele acordate personalului, potrivit legii, pentru protecția socială (423);”
— OMFP 1802/2014, anexa nr. 1, contul 645 (sursă: [OMFP nr. 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate)](https://legislatie.just.ro/Public/DetaliiDocument/164320))
:::

## Ce e confirmat pentru salarizarea obișnuită

La contabilizarea statului de plată, iConta.eu propune notele contabile standard pentru un stat de plată obișnuit: 641/421 (cheltuiala cu salariile), 421/4315 (reținere CAS), 421/4316 (reținere CASS), 421/444 (reținere impozit), 646/436 (cheltuiala CAM a angajatorului), opțional 642/5328 (tichete de masă) și, la part-time sub salariul minim, 6451/4315 și 6453/4316 (cheltuiala de suprataxare a angajatorului).

## Ce se adaugă pentru concediile medicale

Când în luna respectivă există concedii medicale, nota statului de plată mai cuprinde:

- **6458 = 423** — indemnizația suportată de angajator (zilele 1–5, OUG 158/2005 art. 12 lit. A);
- **4382 = 423** — indemnizația suportată din FNUASS (din ziua a 6-a, art. 12 lit. B), ca sumă de recuperat din bugetul FNUASS (art. 38 alin. (1)); contul 4382 „Alte creanțe sociale” e o alegere interpretativă a aplicației: OMFP 1802/2014 prevede, în debitul contului 431, „sumele datorate personalului, ce se suportă din asigurări sociale (423)”, fără să numească analiticul, iar analiticele lui 431 privesc contribuțiile datorate, din care art. 38 alin. (1) nu permite recuperarea;
- **423 = 4315 / 4316 / 444** — CAS, CASS și impozitul reținute din indemnizație; din 421 se rețin doar sumele care privesc salariul, exact cele de pe fluturaș.

Soldul contului 423 după notă trebuie să fie egal cu netul indemnizațiilor de pe fluturași; dacă nu este, aplicația semnalează diferența la contabilizarea statului.

## Ce se greșește în practică

Greșeala frecventă e înregistrarea indemnizației de concediu medical prin aceleași conturi ca salariul obișnuit (421/4315, 421/4316, 421/444), fără să se țină cont de faptul că indemnizația nu urmează mecanica CAS/CASS/impozit a salariului — vezi „Ce venituri intră în baza de calcul a concediului medical?" pentru diferența dintre cele două mecanisme.

## Ce face iConta.eu

Butonul „Contabilizează statul” din ecranul de salarii propune nota contabilă a lunii, ca ciornă: notele salariului obișnuit și, când există concedii medicale, înregistrările pe contul 423 descrise mai sus. Contribuțiile și impozitul se iau din sumele declarate în D112 pentru aceeași lună, iar indemnizațiile din aceleași date ca D112.

[iConta.eu](/)
