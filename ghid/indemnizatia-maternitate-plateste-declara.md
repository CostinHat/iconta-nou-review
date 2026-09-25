---
title: "Indemnizația de maternitate: cine o plătește și cum se declară"
description: "Cine suportă indemnizația pentru concediul de sarcină și lăuzie, pe ce bază se calculează și de ce baza de calcul folosită de iConta.eu vine din statele de plată deja emise."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Indemnizația de maternitate: cine o plătește și cum se declară

Indemnizația de maternitate nu e suportată de angajator din fondul de salarii, ci din bugetul asigurărilor sociale de sănătate — angajatorul are doar rolul de a calcula și depune actele, nu de a plăti din buzunarul firmei. Confuzia cu indemnizațiile suportate direct de angajator (primele zile de concediu medical obișnuit) e frecventă.

## Temeiul legal

::: ghid-temei
„concediul de lăuzie obligatoriu este concediul de 42 de zile pe care salariata mamă are obligația să îl efectueze după naștere, în cadrul concediului pentru sarcină și lăuzie cu durată totală de 126 de zile, de care beneficiază salariatele în condițiile legii"
— OUG 96/2003, art. 2 lit. g) (sursă: anaf_surse/oug_96_2003_protectia_maternitatii_locurile_munca.txt)
:::

Baza de calcul a indemnizațiilor de asigurări sociale de sănătate, inclusiv cea de maternitate, se stabilește potrivit OUG 158/2005:

- Concediul pentru sarcină și lăuzie are o durată totală de **126 de zile**, din care **42 de zile de concediu de lăuzie obligatoriu** trebuie efectuate după naștere.
- Indemnizația se plătește din **bugetul Fondului național unic de asigurări sociale de sănătate**, nu din fondul de salarii al angajatorului — angajatorul depune actele și calculează cererea, dar plata e suportată de stat.
- Baza de calcul a indemnizației se determină ca medie a veniturilor brute lunare din **ultimele 6 luni din cele 12 luni** din care se constituie stagiul de asigurare (OUG 158/2005, art. 10 alin. (1)), pe zile lucrătoare, nu calendaristice.
- Declararea se face prin statul de plată și prin declarația unică privind obligațiile de plată (D112), unde indemnizația apare distinct de veniturile salariale supuse contribuțiilor obișnuite.

## Ce se greșește în practică

- Se calculează media pe 6 luni pe baza salariilor **recalculate azi** (cu cota sau salariul minim actual), nu pe baza sumelor efectiv plătite salariatei în lunile respective — media legală se face pe ce s-a primit efectiv, nu pe o reconstituire ulterioară.
- Se confundă indemnizația de maternitate (suportată de FNUASS) cu primele zile de concediu medical obișnuit, care rămân în sarcina angajatorului — regimul de suportare diferă, iar amestecarea lor denaturează atât fluturașul, cât și D112.
- Se omite includerea în calcul a unei luni pentru care angajatei i s-a emis deja un stat de plată cu o bază diferită de cea recalculată acum, ceea ce produce o indemnizație care nu corespunde niciunei realități efectiv plătite.

## Ce face iConta.eu

La data acestui ghid, iConta.eu calculează baza indemnizației (inclusiv cea de maternitate/concediu medical) plecând de la statele de plată deja **emise**, nu prin recalcul retroactiv: pentru fiecare din cele 6 luni anterioare, aplicația preferă cifrele din statul emis, iar pentru lunile neemise folosește recalculul — dar le numără separat, ca să nu se amestece tacit două tipuri de cifre în aceeași medie (`core/baza_cm.py`). Motivul, explicit în cod: „ce s-a plătit efectiv e un fapt" — media legală (OUG 158/2005 art. 10 alin. (4)) se face pe ce a primit omul, nu pe ce ar rezulta dintr-un calcul refăcut azi. Depunerea efectivă a cererii de concediu și calculul deciziei medicale rămân, în continuare, pe baza documentelor introduse de contabil.

[iConta.eu](/)
