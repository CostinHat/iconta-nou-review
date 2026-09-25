---
title: "Pro-rata pentru ONG-uri cu activitate economică"
description: "Cheltuielile comune ale unui ONG (conducere, administrare) trebuie alocate între activitatea fără scop patrimonial și cea economică printr-o metodă rațională — norma nu impune o formulă fixă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Pro-rata pentru ONG-uri cu activitate economică

Un ONG cu activitate economică nu ține de regulă conturi complet separate pentru fiecare leu de cheltuială — există aproape mereu cheltuieli comune (chirie sediu, salarii de conducere, servicii de contabilitate) care deservesc deopotrivă scopul statutar și activitatea economică. Norma de aplicare a art. 15 din Codul fiscal cere ca acestea să fie alocate, nu ignorate sau deduse integral.

## Temeiul legal

::: ghid-temei
„e) determinarea valorii deductibile a cheltuielilor corespunzătoare veniturilor impozabile de la lit. d), avându-se în vedere următoarele: (i) stabilirea cheltuielilor corespunzătoare veniturilor impozabile de la lit. d) prin scăderea din totalul cheltuielilor a celor aferente activității nonprofit și a unei părți din cheltuielile comune, determinată prin utilizarea unei metode raționale de alocare, potrivit reglementărilor contabile aplicabile; (ii) ajustarea cheltuielilor determinate conform regulilor de la pct. i), luându-se în considerare prevederile art. 25 din Codul fiscal;"
— HG 1/2016, norma la art. 15 pct. 3 lit. e) din Codul fiscal (sursă: anaf_surse/hg_1_2016_norme_cod_fiscal.txt)
:::

- Cheltuielile direct identificabile pe fiecare activitate (statutară vs. economică) se alocă direct — nu se pune problema unei „pro-rata" pentru ele.
- Pentru cheltuielile **comune**, cele care nu pot fi atribuite exclusiv uneia dintre activități, norma cere o „metodă rațională de alocare, potrivit reglementărilor contabile aplicabile" — legea nu impune o formulă unică (de exemplu, nu spune explicit „proporțional cu ponderea veniturilor"), lăsând organizației să documenteze o metodă rezonabilă și consecventă de la un an la altul.
- O metodă frecvent folosită în practică, prin analogie cu alte situații similare din normele fiscale, este alocarea proporțională cu ponderea veniturilor economice în totalul veniturilor — dar orice metodă rațională, documentată și aplicată constant, poate fi susținută.
- Rezultatul alocării se ajustează în continuare potrivit regulilor generale de deductibilitate de la art. 25 din Codul fiscal (cheltuiala trebuie să fie, la rândul ei, făcută în scopul activității economice).

Atenție: acest calcul nu trebuie confundat cu **pro-rata de TVA** (art. 300 din Codul fiscal), care privește dreptul de deducere a TVA la achizițiile destinate deopotrivă operațiunilor cu drept de deducere și fără drept de deducere — un subiect diferit, cu o formulă legală proprie, care nu ține de impozitul pe profit al ONG-urilor.

## Ce se greșește în practică

- Se deduc integral, la activitatea economică, cheltuielile comune de administrare (chirie, salarii de conducere), fără nicio alocare către activitatea fără scop patrimonial.
- Se confundă alocarea cheltuielilor comune de la art. 15 (impozit pe profit) cu pro-rata de TVA (art. 300) — sunt calcule diferite, cu baze și scopuri diferite.
- Se schimbă metoda de alocare de la un an la altul, în funcție de ce iese mai avantajos, în loc să se aplice consecvent o metodă documentată.

## Ce face iConta.eu

Funcționalitatea de contabilitate ONG din iConta.eu (`core/ong.py`) tratează exclusiv **veniturile**: clasificarea veniturilor fără scop patrimonial pe conturile din grupa 73 și calculul plafonului de scutire de la art. 15 alin. (3). **Aplicația nu are nicio funcție de alocare a cheltuielilor comune** între activitatea fără scop patrimonial și cea economică — stabilirea metodei raționale de alocare și aplicarea ei rămân integral în sarcina contabilului, în afara acestei funcționalități.

[iConta.eu](/)
