---
title: Cum se calculează plățile anticipate trimestriale de impozit pe profit?
description: În regimul opțional de declarare anuală, plățile anticipate trimestriale de impozit pe profit se calculează ca 1/4 din impozitul datorat pentru anul precedent, actualizat cu indicele prețurilor de consum — cu excepția trimestrului I, care, începând cu anul fiscal 2026, se calculează pe profitul contabil al perioadei. O formulă diferită de cea a regimului standard. Se declară prin D100, cod 103.
published: 2026-09-22
modified: 2026-10-13
poarta: v1
---

# Cum se calculează plățile anticipate trimestriale de impozit pe profit?

Regimul de declarare anuală, cu plăți anticipate trimestriale, e o opțiune separată de regimul standard trimestrial și folosește o formulă complet diferită de calcul. Confuzia între cele două regimuri e una dintre cele mai frecvente surse de eroare în calculul impozitului pe profit.

## Temeiul legal

::: ghid-temei
**CF art. 41 alin. (2)-(3):**
> „Contribuabilii, alții decât cei prevăzuți la alin. (4) și (5), pot opta pentru calculul, declararea și
> plata impozitului pe profit anual, cu plăți anticipate, efectuate trimestrial... Opțiunea este
> obligatorie pentru cel puțin 2 ani fiscali consecutivi."
— sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282)

**CF art. 41 alin. (8):**
> „Contribuabilii care aplică sistemul de declarare și plată a impozitului pe profit anual, cu plăți
> anticipate efectuate trimestrial, determină plățile anticipate trimestriale în sumă de o pătrime din
> impozitul pe profit datorat pentru anul precedent, actualizat cu indicele prețurilor de consum...
> cu excepția plății anticipate aferente trimestrului IV care se declară și se plătește până la data
> de 25 decembrie, respectiv până la data de 25 a ultimei luni din anul fiscal modificat."
— sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282)

„[...] plata anticipată pentru trimestrul I al fiecărui an fiscal/an fiscal modificat se calculează prin aplicarea cotei de impozit asupra profitului contabil al perioadei pentru care se efectuează plata anticipată. Aceasta se declară și se plătește până la data de 25 inclusiv a lunii următoare trimestrului I.”
— Legea nr. 227/2015 privind Codul fiscal, art. 41 alin. (10^1) (sursă: [Legea nr. 227/2015 privind Codul fiscal](https://legislatie.just.ro/Public/DetaliiDocument/171282))
:::

## Formula regimului opțional, distinctă de cea standard

Spre deosebire de regimul standard (unde baza e profitul efectiv cumulat de la 1 ianuarie, cu regularizare anuală prin D101), regimul opțional cu plăți anticipate calculează fiecare plată trimestrială ca **1/4 din impozitul pe profit datorat pentru anul precedent**, actualizat cu indicele prețurilor de consum — nu pe baza profitului efectiv realizat în trimestrul curent. Începând cu anul fiscal 2026, trimestrul I face excepție: alineatul (10^1) al art. 41, introdus de OUG 8/2026, cere ca plata anticipată pentru trimestrul I să se calculeze aplicând cota de impozit asupra profitului contabil al trimestrului I, nu ca 1/4 din impozitul anului precedent; formula de 1/4 rămâne pentru trimestrele II–IV. O altă excepție e trimestrul IV, care se declară și se plătește până la 25 decembrie (nu 25 a lunii următoare).

Aceste plăți anticipate (inclusiv cea de trimestrul IV, cu scadență 25 decembrie) se declară prin **D100, cod 103** — la fel ca obligațiile trimestriale ale regimului standard, dar calculate cu formula 1/4 descrisă mai sus. D101 rămâne declarația **anuală** de regularizare, depusă la finalul anului fiscal, nu formularul pentru raportarea acestor plăți anticipate trimestriale.

Opțiunea pentru acest regim este obligatorie pentru minimum 2 ani fiscali consecutivi odată aleasă — nu poate fi schimbată de la un trimestru la altul după bunul plac.

## Ce se greșește în practică

- Se calculează plata anticipată pentru trimestrele II–IV pe baza profitului efectiv al trimestrului curent, în loc de 1/4 din impozitul anului precedent — formula regimului standard aplicată greșit peste regimul opțional.
- Se calculează și plata anticipată pentru trimestrul I ca 1/4 din impozitul anului precedent, deși începând cu anul fiscal 2026 ea se calculează aplicând cota de impozit asupra profitului contabil al trimestrului I (CF art. 41 alin. (10^1)).
- Se presupune că aplicația calculează automat formula de 1/4 din impozitul anului precedent pentru firmele care au optat pentru acest regim — verificați manual, vezi mai jos.
- Se schimbă regimul de la un trimestru la altul, deși opțiunea e obligatorie minimum 2 ani fiscali consecutivi.
- Se aplică scadența 25 a lunii următoare și pentru trimestrul IV, deși în regimul opțional trimestrul IV are termen fix 25 decembrie.
- Se crede greșit că aceste plăți anticipate se declară prin D101, deși ele se declară prin D100, cod 103.

## Ce face iConta.eu

Vectorul fiscal al firmei distinge doar între regimurile „micro" și „profit" (regimurile fiscale = ("micro", "profit")) — nu există un atribut separat care să marcheze opțiunea pentru regimul anual cu plăți anticipate trimestriale. Ca urmare, motorul de calcul („calculul obligațiilor (Declarații)”) aplică întotdeauna formula regimului standard — bază cumulată de la 1 ianuarie, nu formula 1/4 din impozitul anului precedent. Dacă firma dvs. a optat oficial pentru regimul cu plăți anticipate trimestriale, calculul acestei formule (inclusiv regula specială pentru trimestrul I) trebuie făcut și verificat manual, în afara declarației generate automat — aplicația nu are astăzi această distincție implementată.

[iConta.eu](/)
