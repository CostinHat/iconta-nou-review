---
title: "Cum se verifică plafonul de trei salarii de bază pentru diurnă?"
description: "Formula celui de-al doilea prag al plafonului de diurnă neimpozabilă — 3 salarii de bază raportate la zilele lucrătoare din lună — și când devine el plafonul efectiv aplicabil."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se verifică plafonul de trei salarii de bază pentru diurnă?

Plafonul de diurnă neimpozabilă are două praguri, iar cel de „2,5 ori diurna bugetară" nu e singurul care contează. Legea impune un al doilea prag, legat de salariul propriu al angajatului — și tocmai acest al doilea prag e cel mai des ignorat în practică, deși poate fi mai restrictiv decât primul.

## Temeiul legal

::: ghid-temei
„în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat. [...] Plafonul aferent valorii a 3 salarii de bază corespunzătoare locului de muncă ocupat se calculează distinct pentru fiecare lună în parte, prin raportarea celor 3 salarii la numărul de zile lucrătoare din luna respectivă, iar rezultatul se multiplică cu numărul de zile corespunzător fiecărei luni din perioada de delegare/detașare/desfășurare a activității în altă localitate, în țară sau în străinătate."
— Codul fiscal, art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Mecanica exactă a celui de-al doilea prag:

- Se pornește de la **3 salarii de bază** ale angajatului (salariul lunar brut din contract, înmulțit cu 3).
- Suma se împarte la **numărul de zile lucrătoare din luna respectivă** — nu la numărul de zile calendaristice, și nu la un număr fix — rezultă un plafon „pe zi lucrătoare".
- Calculul se face **distinct pentru fiecare lună** din perioada delegării — dacă o deplasare se întinde pe două luni, fiecare lună își are propriul plafon zilnic, calculat cu propriile zile lucrătoare.
- Plafonul zilnic astfel obținut se înmulțește cu numărul de zile din acea lună aflate efectiv în delegare.
- **Plafonul neimpozabil final e minimul** dintre acest prag și pragul de 2,5× diurna bugetară (vezi ghidul dedicat formulei 2,5×) — nu se adună, nu se aplică separat.

## Ce se greșește în practică

- Se ignoră complet acest al doilea prag și se folosește doar 2,5× diurna bugetară — pentru un salariu minim sau apropiat de minim, 3 salarii/zile lucrătoare poate fi sub 57,5 lei/zi, deci plafonul real e mai mic decât cel „popular".
- Se împarte la zilele calendaristice ale lunii, nu la zilele lucrătoare — rezultă un plafon zilnic mai mic decât cel legal.
- Se aplică un singur calcul pentru toată perioada delegării, chiar dacă aceasta se întinde pe mai multe luni cu număr diferit de zile lucrătoare — legea cere calcul distinct, lună cu lună.

## Ce face iConta.eu

Formula celor „3 salarii de bază/zile lucrătoare" este implementată în funcția `plafon_diurna` (`core/deconturi.py`), ca al doilea termen al comparației care determină plafonul final (minimul dintre cele două praguri). Există însă o particularitate de proiectare verificată în cod: funcția **nu calculează singură** numărul de zile lucrătoare din calendar — îl primește ca parametru de la apelant. Restul aplicației are o funcție dedicată pentru acest calcul (`core.scadente.zile_lucratoare_luna`, folosită la salarizare și la declarația D112), dar fluxul curent al deconturilor **nu o apelează** — cere numărul de zile lucrătoare direct de la utilizator, dacă și când calculul e invocat.

Ca și celelalte componente ale plafonului, acest calcul **nu apare în interfața iConta** — nu există un ecran care să ceară salariul de bază și numărul de zile lucrătoare pentru a afișa plafonul rezultat. Formula există corect la nivel de motor de calcul (API), dar rămâne, astăzi, un calcul pe care contabilul trebuie să-l facă manual, cu propriile date despre salariul angajatului și zilele lucrătoare din luna deplasării.

[iConta.eu](/)
