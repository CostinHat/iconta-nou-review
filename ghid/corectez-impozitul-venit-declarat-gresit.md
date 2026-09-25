---
title: "Cum corectez impozitul pe venit declarat greșit în D212?"
description: "Impozitul pe venit din D212 se recalculează pe venitul net impozabil corect (după deducerea CAS și CASS datorate) și se corectează prin declarație rectificativă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez impozitul pe venit declarat greșit în D212?

Pentru un PFA la **sistem real**, o eroare de impozit în D212 aproape întotdeauna se propagă dintr-o eroare la CAS sau CASS — pentru că impozitul se aplică pe venitul net RĂMAS după scăderea contribuțiilor sociale datorate, nu pe venitul net brut. La **normă de venit**, regula e diferită: impozitul se aplică direct pe norma ajustată, fără nicio deducere de CAS/CASS.

## Temeiul legal

::: ghid-temei
„Impozitul anual datorat se stabilește de contribuabili în declarația unică privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice pentru veniturile realizate în anul fiscal anterior, prin aplicarea cotei de 10% asupra venitului net anual impozabil determinat potrivit art. 118."
— Codul fiscal (Legea 227/2015), art. 123 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Contribuabilii care realizează venituri din activități independente pentru care venitul net anual se stabilește pe baza normelor de venit au obligația stabilirii impozitului anual datorat, pe baza Declarației unice privind impozitul pe venit și contribuțiile sociale datorate de persoanele fizice prin aplicarea cotei de 10% asupra normei anuale de venit ajustate, după caz."
— Codul fiscal, art. 69^2 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)

„Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce trebuie verificat la recalculare:

- Pentru sistem real, cota de impozit e fixă, 10%, dar baza (venitul net anual impozabil, art. 118 alin. (2) lit. b) CF) rezultă din venitul net minus CAS și CASS datorate pentru anul respectiv — o eroare la oricare din cele două contribuții denaturează automat impozitul.
- Dacă venitul provine din normă de venit, baza impozabilă e norma (ajustată, dacă e cazul), nu venitul efectiv încasat — și, spre deosebire de sistemul real, impozitul de 10% se aplică DIRECT pe norma ajustată, fără să se scadă din ea CAS și CASS (art. 69^2 alin. (1) CF); confundarea celor două formule e ea însăși o sursă de eroare la normă de venit.
- Pentru veniturile din 2025, o eroare de impozit descoperită și corectată până la 15 aprilie 2026, cu plata integrală până la aceeași dată, poate încă beneficia de bonificația de 3% (OUG 8/2026, art. 8).
- Corecția impozitului, ca și cea a CAS/CASS, se face prin declarație rectificativă, în termenul de prescripție (art. 105 coroborat cu art. 110 din Legea 207/2015).

## Ce se greșește în practică

- La sistem real, se recalculează impozitul fără să se recalculeze mai întâi CAS și CASS — dacă baza de contribuții era greșită, impozitul recalculat pe același venit net brut rămâne greșit.
- La sistem real, se aplică 10% direct pe venitul net brut, omițând deducerea CAS/CASS din baza impozabilă (art. 118 alin. (2) lit. b) CF); la normă de venit, greșeala tipică e inversă — se scad CAS/CASS din normă înainte de impozitare, deși legea (art. 69^2 alin. (1) CF) nu o cere, sau se aplică impozitul pe norma nereajustată/neredusă proporțional.
- Se depune rectificativa doar pentru impozit, lăsând CAS/CASS nemodificate, deși la sistem real cele trei sunt interdependente în același formular.

## Ce face iConta.eu

Motorul `core/d212_engine.py` (funcția `calculeaza_d212`) calculează impozitul exact în ordinea cerută de lege pentru **sistem real** (art. 118 alin. (2) lit. b) CF): venit net, apoi CAS și CASS pe bazele lor proprii, apoi impozitul de 10% pe venitul net rămas după scăderea celor două contribuții — nu pe venitul net brut. Calculul e disponibil integral prin `fisa_d212` (`core/rip_api.py`) pentru contribuabilii cu evidență în Registrul-jurnal de încasări și plăți, doar pentru veniturile anilor 2025 și 2026.

Pentru venituri din normă de venit sau din alte surse (chirii, străinătate), unde D212 e completată manual, corecția impozitului rămâne un calcul făcut de contabil, în afara motorului automat — motorul de sistem real nu se aplică normei de venit, a cărei formulă legală (art. 69^2 alin. (1) CF) e diferită.

[iConta.eu](/)
