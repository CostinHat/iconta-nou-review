---
title: "Înființare PFA pentru un contabil independent"
description: "Obligația de a completa Registrul de evidență fiscală pentru PFA care determină venitul net anual în sistem real, pe baza contabilității în partidă simplă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Înființare PFA pentru un contabil independent

Un contabil care alege să lucreze ca persoană fizică autorizată, nu prin propria firmă, intră sub incidența Titlului IV din Codul fiscal — venituri din activități independente. Dincolo de înregistrarea la registrul comerțului, obligația fiscală centrală, valabilă din prima zi de activitate, este ținerea Registrului de evidență fiscală.

## Temeiul legal

::: ghid-temei
„(1) Contribuabilii prevăzuți la titlul IV din Legea nr. 227/2015 privind Codul fiscal, cu modificările și completările ulterioare, denumită în continuare Codul fiscal, pentru care venitul net anual se stabilește în sistem real, în baza datelor din contabilitate, au obligația să completeze Registrul de evidență fiscală în conformitate cu prevederile prezentului ordin. [...]
(2) Contribuabilii care realizează venituri din activități independente pentru care venitul net anual se stabilește pe baza normelor de venit au obligația să completeze în Registrul de evidență fiscală numai partea referitoare la venituri."
— OMFP nr. 3.254 din 19 decembrie 2017 privind Registrul de evidență fiscală pentru persoanele fizice, art. 1 alin. (1), (2) (sursă: anaf_surse/omfp_3254_2017_registru_evidenta_fiscala_persoane_fizice.txt)
:::

Pentru un contabil independent, care de regulă optează pentru determinarea venitului net anual **în sistem real** (nu pe bază de norme de venit, care nu reflectă corect veniturile unei activități de consultanță), obligațiile principale sunt:

- Completarea Registrului de evidență fiscală, pe baza contabilității în partidă simplă, cu veniturile și cheltuielile efective ale activității.
- Dacă activitatea se desfășoară în cadrul unei asocieri fără personalitate juridică (de exemplu doi contabili PFA care colaborează), obligația privind Registrul revine asociatului desemnat care răspunde pentru asociere în fața autorităților.
- Informațiile din Registru stau la baza sumelor înscrise în Declarația unică privind impozitul pe venit și contribuțiile sociale, secțiunea de venituri din activități independente.
- Spre deosebire de contribuabilii care aplică norme de venit (obligați doar la partea de venituri din Registru), un PFA în sistem real trebuie să evidențieze complet atât veniturile, cât și cheltuielile deductibile.

## Ce se greșește în practică

- Se începe activitatea și se emit facturi înainte de a decide regimul de impozitare (normă de venit sau sistem real), deși alegerea influențează direct ce parte din Registrul de evidență fiscală trebuie completată.
- Se confundă contabilitatea în partidă simplă a unui PFA cu contabilitatea în partidă dublă a unui SRL — un PFA nu ține un plan de conturi complet, ci Registrul de evidență fiscală și, dacă e cazul, Registrul-jurnal de încasări și plăți.
- Nu se desemnează un asociat responsabil de Registru atunci când activitatea se desfășoară în asociere, lăsând obligația neclar atribuită între colaboratori.

## Ce face iConta.eu

La data acestui ghid, iConta.eu are un modul dedicat persoanelor fizice care determină venitul net anual în sistem real (`core/registru_evidenta_fiscala.py`), cu funcții pentru validarea datelor de intrare, calculul venitului net (`venit_net`) și generarea registrului pe an (`registru_pf`, `registru_profit`). Aplicația nu gestionează însă pașii de înființare efectivă a PFA la registrul comerțului sau alegerea formei de impozitare (normă de venit vs. sistem real) — acestea rămân decizii luate înainte de a introduce datele în aplicație, iar iConta.eu preia de aici înainte evidența fiscală curentă a activității.

[iConta.eu](/)
