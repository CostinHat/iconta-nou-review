---
title: "Opțiunea pentru impozit micro la înființare: cum procedez"
description: "Condițiile pe care o firmă nou-înființată trebuie să le îndeplinească pentru a opta pentru impozitul pe veniturile microîntreprinderilor încă din primul an fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Opțiunea pentru impozit micro la înființare: cum procedez

O firmă nou-înființată nu e obligată automat la impozit pe profit doar pentru că nu are încă un an fiscal precedent din care să verifice plafonul de venituri — legea îi permite să opteze pentru sistemul micro direct din primul an, dar condiționat de îndeplinirea unor cerințe la momente diferite.

## Temeiul legal

```
::: ghid-temei
„O persoană juridică română care este nou-înființată poate opta să plătească impozit pe veniturile microîntreprinderilor începând cu primul an fiscal, dacă condițiile prevăzute la art. 47 alin. (1) lit. d) și h) sunt îndeplinite la data înregistrării în registrul comerțului, iar cea prevăzută la lit. g) în termen de 90 de zile inclusiv de la data înregistrării persoanei juridice respective. În cazul în care, în acest termen, nu se îndeplinește condiția de la art. 47 alin. (1) lit. g), microîntreprinderea datorează impozit pe profit începând cu trimestrul următor celui în care expiră perioada de 90 de zile."
— Legea nr. 227/2015 privind Codul fiscal, art. 48 alin. (3) (sursă: anaf_surse/oug_8_2026.txt)
:::
```

Ce presupune concret opțiunea, pentru o firmă nouă:

- **Condițiile de la art. 47 alin. (1) lit. d) și h)** — capitalul social deținut de altcineva decât statul/unitățile administrativ-teritoriale, respectiv nu se află în procedură de dizolvare — trebuie îndeplinite **chiar la data înregistrării** la registrul comerțului.
- **Condiția de la lit. g)** — de regulă legată de existența a cel puțin un salariat — are un termen de grație de **90 de zile inclusiv** de la înregistrare, nu trebuie îndeplinită imediat.
- **Dacă nu e îndeplinită condiția salariatului în cele 90 de zile**, firma nu rămâne totuși fără regim fiscal: datorează impozit pe profit, dar abia **din trimestrul următor** celui în care expiră termenul de 90 de zile — nu retroactiv de la înființare.
- Plafonul de venituri de 100.000 euro (art. 47 alin. (1) lit. c)) nu se verifică la firmele nou-înființate în primul lor an fiscal, pentru simplul motiv că nu există încă un exercițiu financiar precedent încheiat — regula prevăzută pentru verificarea anuală se aplică începând cu anul următor.

## Ce se greșește în practică

- Se crede că firma trebuie să aibă deja un salariat angajat chiar din ziua înființării, ca să poată opta pentru micro — de fapt condiția are un termen de grație de 90 de zile.
- Se presupune că, dacă în cele 90 de zile nu s-a angajat niciun salariat, firma datorează impozit pe profit retroactiv, de la data înființării — corect, obligația apare doar din trimestrul următor expirării termenului.
- Se aplică regula plafonului de 100.000 euro și firmelor nou-înființate în același an, deși pentru acestea condiția relevantă la înființare e alta (capital social, absența dizolvării, salariat), nu plafonul de venituri.

## Ce face iConta.eu

Testul propriu al aplicației (`core/test_a8_micro_baza.py`) acoperă doar calculul bazei de impozitare pentru regimul micro (includerea veniturilor din cont 766 și scăderea celor din cont 709) — nu testează și nu implementează verificarea condițiilor de încadrare din art. 47. Nu a fost identificată în cod nicio rutină dedicată verificării condițiilor de eligibilitate pentru regimul micro (art. 47 alin. (1), inclusiv excepția de 90 de zile de la art. 48 alin. (3)) — regimul fiscal rămâne un câmp ales manual de utilizator, iar verificarea acestui termen specific rămâne, la acest moment, o atenție pe care contabilul o acordă manual firmelor aflate în primul lor an de activitate.

[iConta.eu](/)
