---
title: "Cum corectez o diurnă tratată greșit ca neimpozabilă?"
description: "Ce se întâmplă când o diurnă peste plafonul legal a fost înregistrată integral ca neimpozabilă și cum se remediază situația la nivel de salarizare și declarații."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez o diurnă tratată greșit ca neimpozabilă?

Dacă un decont de deplasare a fost înregistrat cu întreaga diurnă trecută pe cheltuială, fără să se verifice plafonul neimpozabil, excedentul peste plafon a rămas netratat ca venit salarial — deci nu s-au calculat impozit, CAS și CASS pentru el, și nu a fost raportat corect la stat. Corecția înseamnă, în esență, recalcularea plafonului pentru fiecare deplasare afectată și tratarea diferenței ca venit salarial suplimentar.

## Temeiul legal

::: ghid-temei
„pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru indemnizație [...], în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat [...]"
— Codul fiscal, art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pașii pe care îi presupune o corecție reală:

- Se recalculează, pentru fiecare deplasare afectată, **plafonul neimpozabil** aplicabil la data respectivă (minimul dintre 2,5× diurna bugetară și 3 salarii/zile lucrătoare) — folosind valorile legale valabile la data deplasării, nu cele curente.
- Diferența dintre diurna efectiv plătită și plafon devine **venit salarial impozabil** — trebuie recalculate impozitul pe venit, CAS și CASS aferente acelei sume, ca pentru orice alt spor de salariu.
- Suma impozabilă recalculată se raportează prin declarația unică pe salarii (D112), la rândul dedicat veniturilor asimilate salariilor peste plafonul de neimpozabilitate.
- Dacă recalcularea privește o perioadă fiscală deja închisă, corecția presupune și depunerea unei declarații rectificative pentru luna/lunile afectate, cu regularizarea sumelor de plată.

## Ce se greșește în practică

- Se corectează doar nota contabilă (se re-postează diferit suma), fără să se recalculeze și obligațiile de impozit/CAS/CASS aferente excedentului.
- Se aplică, la recalculare, plafonul valabil azi, nu cel din perioada deplasării — dacă între timp diurna bugetară s-a modificat, plafonul recalculat trebuie să folosească valoarea istorică, nu cea curentă.
- Se ignoră obligația de a rectifica D112 pentru lunile în care diferența trebuia deja raportată ca venit impozabil.

## Ce face iConta.eu

Acest scenariu de eroare este confirmat direct de comportamentul curent al codului, nu doar teoretic: funcția care generează nota contabilă pentru un decont (`core/deconturi.py`, funcția `nota_decont`) **nu verifică niciodată plafonul** înainte de a posta diurna — întreaga sumă introdusă de utilizator ajunge înregistrată ca o singură cheltuială (625 = 542), indiferent dacă depășește plafonul legal sau nu. Separarea neimpozabil/impozabil există doar ca o funcție de calcul separată (`plafon_diurna`), pe care fluxul de decont nu o apelează automat. Deci, dacă un contabil nu calculează manual plafonul înainte de a introduce diurna, riscul descris de acest ghid — o diurnă peste plafon rămasă înregistrată integral ca „neimpozabilă" — este real și se poate produce exact așa cum e descris mai sus.

Pentru corecția propriu-zisă (stornarea sau editarea notei contabile greșite), iConta.eu folosește mecanismele generale de corecție a notelor contabile din aplicație — acestea nu sunt specifice modulului de deconturi de deplasare și nu sunt tratate în acest ghid. Recalcularea impozitului, CAS și CASS pentru excedent, precum și rectificarea D112, rămân, astăzi, pași pe care contabilul trebuie să-i parcurgă manual — aplicația nu detectează automat o diurnă înregistrată greșit peste plafon și nu oferă un flux dedicat de corecție pentru acest caz specific.

[iConta.eu](/)
