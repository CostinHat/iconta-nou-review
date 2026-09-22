---
title: Înființare firmă și primul angajat - ce contribuții apar?
description: La angajarea primului salariat apar patru contribuții obligatorii - CAS 25%, CASS 10% și impozit 10% reținute din brut, plus CAM 2,25% suportată separat de angajator - fără nicio facilitate sectorială, indiferent de domeniul de activitate.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Înființare firmă și primul angajat - ce contribuții apar?

Odată ce o firmă nou înființată angajează primul salariat, apar automat patru obligații fiscale legate de salarizare, indiferent de domeniul de activitate (codul CAEN) al firmei. Trei dintre ele se rețin din salariul brut al angajatului, iar una este suportată separat de angajator, peste brut.

## Temeiul legal

::: ghid-temei
**Codul fiscal, Articolul 138 lit.a)** — cota de 25% pentru contribuția de asigurări sociale (CAS), aplicabilă persoanelor cu calitate de angajați.

**Codul fiscal, Articolul 156:** *"Cota de contribuție de asigurări sociale de sănătate este de 10%."*

**Codul fiscal, Articolul 78, alin.(2) lit.a):** *"la locul unde se află funcția de bază, prin aplicarea cotei de 10% asupra bazei de calcul..."*

**Codul fiscal, Articolul 220^3, alin.(1):** *"Cota contribuției asiguratorii pentru muncă este de 2,25%."*

**Codul fiscal, Articolul 60, pct.2 (scutire IT/software):** *"Abrogat. (la 01-01-2025, Punctul 2., Articolul 60... a fost abrogat de Punctul 7., Articolul LXIV din ORDONANȚA DE URGENȚĂ nr. 156 din 30 decembrie 2024...)"*
:::

## Cele patru contribuții

- **CAS (25%)** și **CASS (10%)** se rețin din venitul brut impozabil al angajatului și se plătesc din salariul acestuia, nu suplimentar de angajator.
- **Impozitul pe venit (10%)** se calculează pe baza impozabilă rămasă după scăderea CAS, CASS și a deducerii personale, și se reține tot din salariul angajatului.
- **CAM — Contribuția asiguratorie pentru muncă (2,25%)** este singura contribuție suportată integral de angajator, peste salariul brut, calculată la venitul brut total impozabil.

Pe lângă acestea, dacă firma plătește primul angajat exact la nivelul salariului minim brut pe țară, poate beneficia de facilitatea de 200/300 lei/lună (scutire de impozit și contribuții pe această sumă), condiționată de patru criterii cumulative din lege — vezi ghidul dedicat facilității pentru salariul minim.

Un aspect esențial pentru firmele nou înființate, mai ales cele din IT, este că **nu mai există nicio facilitate sectorială** legată de domeniul de activitate. Scutirile istorice pentru IT/software, construcții și agricultură/industrie alimentară au fost eliminate simultan de la 01.01.2025.

::: ghid-exemplu
Un angajat cu normă întreagă, plătit cu salariul brut de 5.000 lei, generează pentru firmă: CAS 1.250 lei + CASS 500 lei + impozit (pe baza impozabilă rămasă, după deducere) reținute din brut, iar angajatorul plătește separat CAM = 5.000 × 2,25% = 112,50 lei.
:::

## Ce se greșește în practică

- Se presupune că, la înființarea firmei, se poate alege o schemă de contribuții reduse dacă domeniul de activitate e IT, construcții sau agricultură — aceste facilități au fost abrogate de la 01.01.2025.
- Se uită de CAM, considerând că angajatorul plătește doar salariul brut către angajat, fără nicio obligație suplimentară.
- Se calculează CAM la salariul net, nu la venitul brut total impozabil.
- Se confundă CAS și CASS (ambele rețineri din brut) cu CAM (obligație separată, exclusiv a angajatorului).

## Ce face iConta.eu

Motorul de calcul (`calcul_salariu()`) aplică cele patru contribuții pe baza cotelor curente din registrul intern: CAS 25% și CASS 10% pe baza de contribuție (brutul impozabil, eventual redus de facilitatea salariului minim), impozit 10% pe baza impozabilă rămasă după deducerea personală, și CAM 2,25% pe brutul total impozabil, calculat și afișat separat, ca sarcină a angajatorului. Aplicația nu implementează nicio ramură de scutire pe cod CAEN — corect, întrucât nicio astfel de scutire nu mai are temei legal din 2025.

[iConta.eu](/)
