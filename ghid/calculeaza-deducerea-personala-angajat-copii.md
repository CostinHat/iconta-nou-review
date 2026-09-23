---
title: Cum se calculează deducerea personală pentru un angajat cu copii?
description: Fiecare copil în întreținere crește procentul deducerii (25/30/35/45%, după numărul de persoane în întreținere); pe lângă asta, există o deducere separată de 100 lei/lună/copil la învățământ, condiționată de declarație — nu se acordă automat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează deducerea personală pentru un angajat cu copii?

Copiii aflați în întreținerea angajatului cresc procentul deducerii personale, față de scara de bază (fără persoane în întreținere). Pe lângă acest efect, legea prevede și o sumă fixă separată — 100 lei/lună pentru fiecare copil înscris la învățământ — dar aceasta e condiționată strict de documente, nu se acordă din oficiu.

## Temeiul legal

::: ghid-temei
Codul fiscal (Legea 227/2015), art.77 alin.(4): scara deducerii crește cu numărul persoanelor aflate în întreținere (20/25/30/35/45%, pentru 0/1/2/3/4 sau mai multe persoane); alin.(10) lit.b): se acordă suplimentar 100 lei/lună pentru fiecare copil minor înscris într-o unitate de învățământ, indiferent de nivelul venitului, condiționat de alin.(12)-(13) — document de înscriere plus declarație pe propria răspundere a părintelui.
:::

## Scara deducerii, cu copii ca persoane în întreținere

Cât timp venitul brut lunar e sub sau egal cu salariul minim aplicabil lunii, deducerea se acordă la procentul maxim din scară, raportat la salariul minim al lunii respective. Pentru 2026, salariul minim are două valori — 4.050 lei (1 ianuarie – 30 iunie) și 4.325 lei (1 iulie – 31 decembrie):

| Copii în întreținere | Procent | Deducere ian–iun 2026 (min. 4.050 lei) | Deducere iul–dec 2026 (min. 4.325 lei) |
|---|---|---|---|
| 1 | 25% | 1.012,50 lei | 1.081,25 lei |
| 2 | 30% | 1.215,00 lei | 1.297,50 lei |
| 3 | 35% | 1.417,50 lei | 1.513,75 lei |
| 4 sau mai mulți | 45% | 1.822,50 lei | 1.946,25 lei |

**Exemplu**: un angajat cu funcție de bază, 1 copil în întreținere, venit brut lunar la nivelul salariului minim din fereastra iulie–decembrie 2026 (4.325 lei), primește o deducere de bază de 25% × 4.325 = **1.081,25 lei**.

Peste salariul minim, procentul scade degresiv (0,5 puncte pentru fiecare tranșă de 50 lei peste minim), până se anulează la pragul salariul minim + 2.000 lei — același mecanism ca la deducerea fără persoane în întreținere.

## Deducerea separată de 100 lei/lună/copil la învățământ

Această sumă e distinctă de scara de mai sus — se adaugă la deducerea calculată după numărul de persoane în întreținere, indiferent de nivelul venitului brut. Dar legea o condiționează obligatoriu de:

- un document care confirmă înscrierea copilului la o unitate de învățământ, și
- o declarație pe propria răspundere a părintelui (dacă părintele are mai mulți angajatori, și declarația că nu beneficiază de deducere la celălalt angajator).

**De semnalat onest**: codul motorului de calcul verificat pentru acest ghid are un gard explicit care refuză acordarea deducerii de 100 lei/copil fără declarația pe propria răspundere bifată — implementează literal condiția legală de mai sus. Datele reale de intrare pentru această deducere (numărul de copii la învățământ, existența declarației) sunt confirmate ca fiind citite și transmise motorului de calcul de către componenta care generează efectiv statul de plată. Totuși, în codul sursă rămâne un semnal de „funcționalitate necablată" pe partea de introducere a datelor, iar niciun ecran dedicat statului de plată n-a putut fi identificat direct în acest dosar — deci nu putem confirma cu certitudine dacă, în interfața curentă, angajatorul poate introduce efectiv aceste date de la un capăt la altul. Verificați direct în aplicație dacă opțiunea „copil la învățământ + declarație" e disponibilă la completarea datelor angajatului.

## Ce se greșește în practică

- Se confundă cele două deduceri: scara de bază (care crește procentul cu numărul de persoane în întreținere) și suma fixă de 100 lei/copil la învățământ (care se adaugă separat, condiționat de documente) — nu sunt același lucru.
- Se acordă deducerea de 100 lei/copil fără documentul de înscriere sau fără declarația pe propria răspundere.
- Se aplică procentul din scară raportat la salariul minim greșit (se folosește o singură valoare pentru tot 2026, în loc de a verifica fereastra — 4.050 sau 4.325 lei — corespunzătoare lunii calculate).

## Ce face iConta.eu

Deducerea calculată după numărul de persoane în întreținere e acoperită integral de `deducere_personala()` din `core/salarizare.py`, folosind registrul „period-aware" de cote și praguri. Pentru deducerea de 100 lei/copil la învățământ, codul are un gard defensiv care respinge introducerea unui număr de copii la învățământ fără declarația pe propria răspundere bifată — regula legală e implementată strict, nu se acordă tacit.

[iConta.eu](/)
