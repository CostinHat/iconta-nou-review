---
title: "Concediul de odihnă 2026: cum se calculează indemnizația"
description: "Formula legală de calcul a indemnizației de concediu de odihnă — media zilnică a veniturilor înmulțită cu zilele de concediu — și termenul de plată."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Concediul de odihnă 2026: cum se calculează indemnizația

Indemnizația de concediu de odihnă nu e salariul obișnuit al lunii — e un calcul separat, bazat pe media veniturilor, care poate diferi de salariul de bază atunci când angajatul are variații salariale (sporuri, bonusuri) de la o lună la alta.

## Temeiul legal

::: ghid-temei
„(1) Pentru perioada concediului de odihnă salariatul beneficiază de o indemnizaţie de concediu care nu poate fi mai mica decât valoarea totală a drepturilor salariale cuvenite pentru perioada respectiva.
(2) Indemnizaţia de concediu de odihnă reprezintă media zilnica a veniturilor din luna/lunile în care este efectuat concediul, multiplicata cu numărul de zile de concediu.
(3) Indemnizaţia de concediu de odihnă se plăteşte de către angajator cu cel puţin 5 zile lucrătoare înainte de plecarea în concediu."
— Legea 53/2003 (Codul muncii), art. 145 alin. (1)-(3) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

Ce rezultă concret din formulă:

- **Baza de calcul e media zilnică a veniturilor din luna/lunile în care se efectuează concediul** — nu media pe un interval fix retroactiv (ex. ultimele 3 luni), ci veniturile din perioada în care se ia efectiv concediul.
- **Formula e simplă**: media zilnică × numărul de zile de concediu efectuate — dar „media zilnică a veniturilor" include, în funcție de politica salarială a firmei, elementele care fac parte din drepturile salariale cuvenite, nu doar salariul de bază.
- **Există o limită minimă**: indemnizația nu poate fi mai mică decât valoarea totală a drepturilor salariale cuvenite pentru perioada respectivă — deci angajatul nu poate ieși în pierdere financiară doar pentru că a plecat în concediu.
- **Termenul de plată e strict**: cu cel puțin 5 zile lucrătoare înainte de plecarea în concediu, nu odată cu salariul lunii — o eventuală întârziere a acestei plăți e o încălcare distinctă de întârzierea salariului obișnuit.

## Ce se greșește în practică

- Se calculează indemnizația din salariul de bază al lunii curente, ignorând că formula legală cere media veniturilor din luna/lunile în care se efectuează concediul, care poate include și alte elemente salariale variabile.
- Se plătește indemnizația odată cu salariul lunii, la data obișnuită de salarizare, în loc de cu cel puțin 5 zile lucrătoare înainte de plecarea efectivă în concediu.
- Se presupune că indemnizația poate fi mai mică decât salariul obișnuit al perioadei, dacă media calculată iese sub acesta — legea impune explicit un prag minim: valoarea totală a drepturilor salariale cuvenite pentru acea perioadă.
- Se confundă indemnizația de concediu de odihnă cu indemnizația de concediu medical — cele două au baze legale și formule de calcul complet diferite (Codul muncii, respectiv OUG 158/2005).

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează salariul obișnuit (`core/salarizare.py`, `calcul_salariu()`) și indemnizația de concediu medical (`calcul_cm()`, cu regulile OUG 158/2005 și Codul fiscal), dar **nu are o funcție dedicată calculului indemnizației de concediu de odihnă** conform formulei „media zilnică a veniturilor × zile de concediu" din art. 145 din Codul muncii. Modulul de pontaj (`core/pontaj.py`) urmărește zilele lucrate și grila de lucru, dar nu generează automat suma de plată pentru zilele de concediu de odihnă. Calculul indemnizației și respectarea termenului de plată de 5 zile lucrătoare înainte de concediu rămân, la acest moment, în sarcina angajatorului/contabilului.

[iConta.eu](/)
