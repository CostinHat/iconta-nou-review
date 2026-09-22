---
title: Rezultatele inventarierii — aprobare și înregistrare
description: Rezultatele inventarierii trec întâi prin decizia administratorilor — cine impută lipsurile și ce sorturi se compensează (OMFP 2861/2009 pct. 40) — și abia apoi se înregistrează în contabilitate, cu note diferite pentru plus, minus imputabil și minus neimputabil.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se aprobă și se înregistrează rezultatele inventarierii?

Lista de inventariere semnată de comisie nu e ultimul pas. Rezultatele — plusuri, lipsuri, eventuale compensări — trebuie mai întâi stabilite de administratori: ce se compensează, cui se impută o lipsă și la ce valoare. Abia după această decizie se pot face notele contabile, iar acestea diferă fundamental după cum diferența e plus, minus imputabil sau minus neimputabil.

## Temeiul legal

::: ghid-temei
**OMFP 2861/2009, Anexă, pct. 40 alin. (1)-(2)**: *„40. - (1) În situația constatării unor plusuri în gestiune, bunurile respective se evaluează potrivit reglementărilor contabile aplicabile. (2) În cazul constatării unor lipsuri imputabile în gestiune, administratorii trebuie să impute persoanelor vinovate bunurile lipsă la valoarea lor de înlocuire."*

**pct. 40 alin. (5)**: *„Listele cu sorturile de produse, mărfuri, ambalaje și alte valori materiale care întrunesc condițiile de compensare datorită riscului de confuzie se aprobă anual de către administratori... Compensarea se face pentru cantități egale între plusurile și lipsurile constatate."*

**pct. 41 alin. (3)**: *„Pentru pagubele constatate în gestiune răspund persoanele vinovate de producerea lor. Imputarea acestora se face la valoarea de înlocuire."*

**HG 1/2016 (Norme CF) pct. 78 alin. (6) lit. a)**: *„...bunuri lipsă în gestiune din alte cauze decât cele prevăzute la art. 304 alin. (2) din Codul fiscal. În cazul bunurilor lipsă din gestiune care sunt imputate, sumele imputate nu sunt considerate contravaloarea unor operațiuni în sfera de aplicare a TVA, indiferent dacă pentru acestea este sau nu obligatorie ajustarea taxei."*

**CF art. 304 alin. (2) lit. a)**: *„Nu se ajustează deducerea inițială a taxei în cazul: a) bunurilor distruse, pierdute sau furate, în condițiile în care aceste situații sunt demonstrate sau confirmate în mod corespunzător de persoana impozabilă."*
:::

## Ce aprobă administratorii, înainte de înregistrare

Administratorii nu doar "iau la cunoștință" rezultatul inventarierii — legea le pune explicit în sarcină două decizii, înainte ca sumele să ajungă în contabilitate:

1. **Cui se impută o lipsă și la ce valoare.** Pct. 40 alin. (2) e clar: administratorii trebuie să impute persoanelor vinovate bunurile lipsă la valoarea lor de înlocuire — nu la valoarea contabilă.
2. **Ce sorturi intră pe lista de compensare.** Listele cu sorturile eligibile pentru compensare pe risc de confuzie se aprobă anual, nu ad-hoc, la fiecare inventar.

## Cum se înregistrează fiecare tip de rezultat

**Plusul** se evaluează potrivit reglementărilor contabile aplicabile și intră în gestiune.

**Minusul, indiferent dacă e imputabil sau nu**, se descarcă din gestiune la valoarea contabilă: `60x = 3xx` (de exemplu `607 = 371` pentru mărfuri).

**Dacă minusul e imputabil**, se adaugă separat creanța față de vinovat, la valoarea de înlocuire stabilită de administratori: `4282 = 7581` dacă e salariat, `461 = 7581` dacă e terț. Sumele imputate nu sunt, potrivit pct. 78 alin. (6) lit. a) din normele Codului fiscal, contravaloarea unei operațiuni în sfera TVA — deci imputarea nu generează TVA colectată.

**Ajustarea TVA deductibile** e o operațiune separată, legată de lipsa bunului din gestiune ca atare, nu de imputare: dacă lipsa nu se încadrează la excepțiile de la art. 304 alin. (2) lit. a) (bun distrus, pierdut sau furat, demonstrat corespunzător), TVA deductibilă deja exercitată la achiziția bunului lipsă trebuie ajustată, prin `635 = 4426`. Această ajustare se face indiferent dacă lipsa e sau nu imputată — cele două lucruri, imputarea și ajustarea de TVA, sunt independente una de alta.

## Ce se greșește în practică

- **Se înregistrează imputarea ca și cum ar fi o vânzare cu TVA**, adăugând `4427` pe valoarea imputată — legea spune explicit contrariul.
- **Se sare peste ajustarea TVA deductibile** pe motiv că lipsa oricum se recuperează de la vinovat — imputarea și ajustarea de TVA sunt două operațiuni distincte, iar a doua nu depinde de prima.
- **Se aprobă compensarea ad-hoc, la fața locului**, fără o listă de sorturi aprobată anual de administratori — condiție cerută expres de pct. 40 alin. (5).

## Ce face iConta.eu

Aplicația generează separat notele de descărcare de gestiune la valoarea contabilă pentru minusuri și nota de evaluare pentru plusuri, pe baza rezultatelor introduse din listele de inventariere. Decizia administratorilor privind cine răspunde de o lipsă imputabilă, valoarea de înlocuire stabilită și lista anuală de compensare rămân decizii de aprobat separat, în afara aplicației, înainte de a fi introduse ca date de intrare. Tratamentul de TVA aplicat efectiv pe lipsurile imputabile — atât partea de TVA colectată la imputare, cât și ajustarea TVA deductibile — este în verificare și nu trebuie considerat conform până la confirmare separată.

[iConta.eu](/)
