---
title: "Cum se calculează indemnizația de concediu de odihnă?"
description: "Formula legală a indemnizației de concediu de odihnă — media zilnică a lunii în care se efectuează concediul, înmulțită cu zilele — și termenul de plată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează indemnizația de concediu de odihnă?

Spre deosebire de indemnizația de concediu medical, care se calculează dintr-o medie pe 6 luni istorice, indemnizația de concediu de odihnă se raportează la o singură perioadă: **luna în care concediul chiar se efectuează**. Formula e simplă, dar des greșită la aplicare.

## Temeiul legal

::: ghid-temei
„Pentru perioada concediului de odihnă salariatul beneficiază de o indemnizaţie de concediu care nu poate fi mai mica decât valoarea totală a drepturilor salariale cuvenite pentru perioada respectiva. [...] Indemnizaţia de concediu de odihnă reprezintă media zilnica a veniturilor din luna/lunile în care este efectuat concediul, multiplicata cu numărul de zile de concediu. [...] Indemnizaţia de concediu de odihnă se plăteşte de către angajator cu cel puţin 5 zile lucrătoare înainte de plecarea în concediu."
— Legea 53/2003 (Codul muncii), art. 145 alin. (1)-(3) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

Din text rezultă exact ce se ia în calcul:

- **Baza** nu e salariul unei luni oarecare, ci **media zilnică a veniturilor din luna sau lunile în care se efectuează concediul** — dacă salariul din luna respectivă diferă de cel obișnuit (mărire, spor nou), acea diferență contează.
- **Indemnizația = media zilnică × numărul de zile de concediu** efectuate.
- Legea garantează un prag minim: indemnizația **nu poate fi mai mică decât valoarea drepturilor salariale cuvenite** pentru aceeași perioadă, dacă salariatul ar fi lucrat.
- Termenul de plată e independent de data obișnuită de salarizare: **cu cel puțin 5 zile lucrătoare înainte de plecarea în concediu**, nu la finalul lunii.

## Ce se greșește în practică

- Se calculează indemnizația din media salariului ultimelor luni anterioare concediului, în loc de media veniturilor din luna în care concediul se efectuează efectiv.
- Se plătește indemnizația odată cu salariul lunii, ignorând termenul legal de 5 zile lucrătoare înainte de plecarea în concediu.
- Se calculează media zilnică prin împărțire la numărul de zile calendaristice ale lunii, nu la zilele lucrătoare relevante pentru determinarea veniturilor zilnice.

## Ce face iConta.eu

iConta.eu nu are un calcul automat, dedicat, al indemnizației de concediu de odihnă pornind de la zilele de concediu programate ale unui salariat — verificat în cod, nu există nicio funcție care să deriveze automat media zilnică a lunii de concediu și s-o înmulțească cu zilele. Contabilul calculează separat suma (conform formulei de mai sus) și o introduce ca parte a venitului brut al lunii; de acolo, motorul de calcul al salariului (`core/salarizare.py`, `calcul_salariu`) preia suma și aplică restul: contribuții, impozit, notă contabilă, fluturaș.

[iConta.eu](/)
