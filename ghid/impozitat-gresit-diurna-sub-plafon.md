---
title: "Am impozitat greșit diurna sub plafon"
description: "Cum se calculează corect plafonul neimpozabil al diurnei interne, ca să nu se impoziteze o sumă care era, de fapt, sub plafon."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Am impozitat greșit diurna sub plafon

Diurna nu se compară direct cu un singur plafon fix. Plafonul neimpozabil e cel mai mic dintre două limite — de 2,5 ori diurna bugetară și de 3 salarii de bază pe zilele lucrătoare din lună — iar o greșeală frecventă e aplicarea unei singure limite, ceea ce poate duce la impozitarea unei sume care, de fapt, era sub plafonul legal.

## Temeiul legal

::: ghid-temei
„indemnizația de delegare, indemnizația de detașare, [...] precum și orice alte sume de aceeași natură, altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare, primite de salariați potrivit legislației în materie, pe perioada desfășurării activității în altă localitate, în țară sau în străinătate, în interesul serviciului, pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru indemnizație, prin hotărâre a Guvernului, pentru personalul autorităților și instituțiilor publice, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat; [...] Plafonul aferent valorii a 3 salarii de bază corespunzătoare locului de muncă ocupat se calculează distinct pentru fiecare lună în parte, prin raportarea celor 3 salarii la numărul de zile lucrătoare din luna respectivă."
— Legea nr. 227/2015 (Codul fiscal), art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Concret, plafonul zilnic neimpozabil e minimul dintre:

- **2,5 × diurna bugetară internă** — 23 lei/zi începând cu 1 aprilie 2023 (Ordin MF nr. 1235/2023), ceea ce dă un plafon de 57,5 lei/zi; anterior, 20 lei/zi (HG nr. 714/2018), plafon de 50 lei/zi.
- **3 × salariul de bază / zilele lucrătoare din lună** — limita raportată la salariul individual al angajatului.
- Suma acordată **peste** minimul acestor două limite devine venit salarial impozabil, supus impozitului, CAS și CASS, și se declară în D112.
- Pentru diurna externă, plafonul bugetar de referință e cel din HG nr. 518/1995, diferit pe fiecare țară.

## Ce se greșește în practică

- Se aplică doar plafonul de 2,5× diurna bugetară, ignorând complet limita de 3 salarii — care poate fi, pentru salariile mici, mai restrictivă și deci relevantă.
- Se folosește, din obișnuință, valoarea veche de 20 lei/zi pentru diurna bugetară internă, deși de la 1 aprilie 2023 valoarea de referință e 23 lei/zi.
- Se impozitează întreaga diurnă „ca să fie sigur", deși suma acordată se încadra, de fapt, sub plafonul minim calculat corect — ceea ce înseamnă impozit, CAS și CASS reținute nejustificat din venitul salariatului.

## Ce face iConta.eu

iConta.eu are o funcție separată care calculează plafonul neimpozabil al diurnei ca minimul dintre 2,5× diurna bugetară internă (versionată — 23 lei/zi din 1 aprilie 2023, 20 lei/zi anterior) și 3× salariul de bază raportat la zilele lucrătoare din lună (`core/deconturi.py`, funcția `plafon_diurna`), returnând distinct suma neimpozabilă și suma impozabilă. Nota contabilă de decont generată de aplicație (625 = 542, cu TVA pe cazare/transport dacă e cazul, prin funcția `nota_decont`) nu preia însă automat această împărțire — postează integral diurna, transportul și cazarea pe cheltuială (625), fără să separe și să treacă prin statul de plată partea de diurnă care depășește plafonul neimpozabil. Verificarea plafonului rămâne, la acest moment, un calcul separat pe care contabilul trebuie să-l coreleze manual cu nota de decont, pentru a evita atât impozitarea unei sume sub plafon, cât și omiterea impozitării excedentului.

[iConta.eu](/)
