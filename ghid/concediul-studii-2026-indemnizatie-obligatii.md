---
title: "Concediul de studii 2026: indemnizație și obligații"
description: "Diferența dintre concediul fără plată pentru formare profesională și cel plătit de până la 10 zile lucrătoare, cu regulile de acordare din Codul muncii, valabile în 2026."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Concediul de studii 2026: indemnizație și obligații

„Concediu de studii" nu e un singur tip de concediu, ci o denumire generică pentru concediile pentru formare profesională reglementate de Codul muncii. Ele pot fi cu plată sau fără plată, iar regulile de acordare, durata și obligația angajatorului diferă radical între cele două variante.

## Temeiul legal

::: ghid-temei
„Articolul 149
(1) Salariaţii au dreptul sa beneficieze, la cerere, de concedii pentru formare profesională.
(2) Concediile pentru formare profesională se pot acorda cu sau fără plata.
Articolul 150
(1) Concediile fără plata pentru formare profesională se acordă la solicitarea salariatului, pe perioada formării profesionale pe care salariatul o urmează din iniţiativa sa.
(2) Angajatorul poate respinge solicitarea salariatului numai cu acordul sindicatului sau, după caz, cu acordul reprezentanţilor salariaţilor şi numai dacă absenta salariatului ar prejudicia grav desfăşurarea activităţii.
Articolul 152
(1) În cazul în care în cursul unui an calendaristic, pentru salariaţii în vârsta de până la 25 de ani, şi, respectiv, în cursul a 2 ani calendaristici consecutivi, pentru salariaţii în vârsta de peste 25 de ani, nu a fost asigurata participarea la o formare profesională pe cheltuiala angajatorului, salariatul în cauza are dreptul la un concediu pentru formare profesională, plătit de angajator, de până la 10 zile lucrătoare."
— Legea nr. 53/2003 (Codul muncii), art. 149 alin. (1), (2), art. 150 alin. (1), (2), art. 152 alin. (1) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

Practic, în 2026 rămân valabile două trasee complet diferite:

- **Concediul fără plată** (art. 150-151) se acordă la cererea salariatului, pentru formarea profesională pe care acesta o urmează din proprie inițiativă. Cererea trebuie depusă cu cel puțin o lună înainte, iar angajatorul poate refuza doar cu acordul sindicatului/reprezentanților salariaților și doar dacă absența ar prejudicia grav activitatea.
- **Concediul plătit de până la 10 zile lucrătoare** (art. 152) e un drept distinct, care apare doar dacă angajatorul nu a asigurat salariatului acces la formare profesională pe cheltuiala sa — într-un an calendaristic, pentru salariații sub 25 de ani, sau în 2 ani consecutivi, pentru cei peste 25 de ani. Indemnizația se calculează potrivit art. 145 (ca indemnizația de concediu de odihnă).
- Durata oricărui concediu pentru formare profesională **nu se scade din concediul de odihnă anual** și e asimilată perioadei de muncă efectivă pentru toate drepturile salariatului, altele decât salariul (art. 153).

## Ce se greșește în practică

- Se confundă cele două tipuri de concediu, plătindu-se un concediu de formare profesională solicitat din inițiativa salariatului, deși legea îl prevede ca fără plată.
- Nu se verifică dacă angajatorul a asigurat efectiv accesul la formare profesională în perioada de referință (1 an sub 25 ani / 2 ani peste 25 ani) înainte de a respinge cererea de concediu plătit de 10 zile.
- Se scade concediul pentru formare profesională din zilele de concediu de odihnă anual, deși art. 153 interzice expres această practică.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are un cod de concediu dedicat pentru formarea profesională** în ecranul de pontaj/stat de plată. Aplicația gestionează concediile medicale pe coduri specifice (de exemplu risc maternal, cod 15, urmărit în `core/nomenclator_cm.py` și `core/d112.py`), dar concediul pentru formare profesională — cu sau fără plată — nu are un flux automatizat propriu; înregistrarea lui în pontaj și, dacă e plătit, calculul indemnizației conform art. 145, rămân o operațiune manuală a contabilului sau a persoanei responsabile de salarizare.

[iConta.eu](/)
