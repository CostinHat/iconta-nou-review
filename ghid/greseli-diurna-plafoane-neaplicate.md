---
title: "Greșeli la diurnă: plafoane neaplicate"
description: "Cea mai frecventă greșeală la decontarea diurnei — omiterea verificării plafonului neimpozabil — și de ce ea nu ține doar de neatenția contabilului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Greșeli la diurnă: plafoane neaplicate

Cea mai comună greșeală la decontarea diurnei nu e o eroare de calcul, ci o eroare de omisiune: diurna e introdusă și înregistrată integral, fără ca cineva să se oprească și să verifice dacă depășește plafonul neimpozabil. Efectul e o sumă de venit impozabil care rămâne netratată ca atare — impozit, CAS și CASS necalculate, nedeclarate.

## Temeiul legal

::: ghid-temei
„pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru indemnizație, prin hotărâre a Guvernului, pentru personalul autorităților și instituțiilor publice, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat [...]"
— Codul fiscal, art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

De ce plafonul „neaplicat" e o greșeală cu consecințe reale, nu doar formale:

- Legea nu lasă la latitudinea firmei dacă aplică sau nu plafonul — partea de diurnă **care depășește** plafonul este, prin definiție legală, venit salarial, nu o chestiune de politică internă.
- Omiterea verificării plafonului înseamnă, de fapt, omiterea calculării impozitului pe venit, CAS și CASS pentru excedent — o obligație fiscală reală, nu doar o formalitate contabilă.
- Plafonul are **două componente** (2,5× diurna bugetară și 3 salarii de bază/zile lucrătoare), iar greșeala „plafon neaplicat" apare de multe ori nu din ignoranță totală, ci din aplicarea doar a primei componente și omiterea celei de-a doua.
- La un control, diferența netratată ca venit impozabil generează obligații de plată recalculate, plus dobânzi și penalități de întârziere pentru perioada în care obligația nu a fost declarată.

## Ce se greșește în practică

- Diurna se introduce și se înregistrează ca o singură cheltuială, fără niciun pas separat de verificare a plafonului.
- Se presupune că „diurna e mereu neimpozabilă", o generalizare falsă — doar partea de sub plafon are acest regim.
- Se verifică doar unul dintre cele două praguri ale plafonului (de regulă 2,5× diurna bugetară), ignorând că cel de 3 salarii/zile lucrătoare poate fi mai restrictiv pentru salariile mici.
- Se aplică diurna bugetară curentă la calculul plafonului, chiar și pentru deplasări din perioade cu o valoare legală diferită.

## Ce face iConta.eu

Acest ghid descrie exact un risc confirmat prin verificarea codului sursă al aplicației, nu doar o recomandare generică: funcția care generează nota contabilă a unui decont (`nota_decont`, din `core/deconturi.py`) **nu apelează niciodată** funcția de calcul al plafonului (`plafon_diurna`) și postează întreaga sumă de diurnă introdusă ca o singură cheltuială, oricât de mare ar fi ea. Cu alte cuvinte, aplicația însăși nu aplică automat plafonul la momentul înregistrării decontului — exact greșeala descrisă de titlul acestui ghid se poate produce dacă operatorul nu calculează manual plafonul înainte de a introduce suma.

E important să se știe clar acest lucru, pentru că se poate crede greșit — pe baza unor descrieri mai vechi ale funcționalității — că „aplicația calculează automat plafonul de diurnă și generează notele corect". Nu este cazul astăzi: calculul de plafon există ca funcție separată, accesibilă doar prin API, fără niciun ecran dedicat, iar decontul propriu-zis se înregistrează integral, fără split automat neimpozabil/impozabil. Contabilul rămâne responsabil să calculeze plafonul manual, înainte de a introduce diurna în ecranul „Decont deplasare / diurnă", pentru a evita exact greșeala descrisă mai sus.

[iConta.eu](/)
