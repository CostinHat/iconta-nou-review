---
title: Cum se calculează perisabilitatea la alimente
description: "Formula e simplă — limita se aplică la valoarea alimentelor intrate, nu la stocul final — dar coeficientul pe grupă de alimente vine din anexa HG 831/2004, nu dintr-un procent general."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează perisabilitatea la alimente

Calculul perisabilității la alimente cumpărate spre revânzare (produse ambalate, băuturi etc., aflate în procesul de comercializare) urmează o formulă fixă, dar cu o variabilă esențială: coeficientul de perisabilitate pe grupa de alimente, care nu e universal — diferă de la o grupă la alta și se caută în anexa hotărârii, nu se aplică un procent „tipic".

## Temeiul legal

::: ghid-temei
„Se aprobă Normele privind limitele admisibile de perisabilitate la mărfuri în procesul de comercializare, prevăzute în anexa care face parte integrantă din prezenta hotărâre."

*(HG nr. 831/2004, art. 1)*
:::

## Formula, pas cu pas

1. **`limita = valoare_intrări × procent_limită / 100`** — se aplică la valoarea de înregistrare a alimentelor intrate în perioadă (nu la stocul rămas, nu la valoarea constatată lipsă).
2. **`deductibil = min(pierdere_constatată, limita)`** — partea din pierdere care nu depășește limita e integral deductibilă.
3. **`nedeductibil = pierdere_constatată − deductibil`** — dacă pierderea depășește limita, diferența e nedeductibilă și, suplimentar, atrage ajustare de TVA (635=4426), calculată la cota aplicabilă, cu excepția degradării calitative dovedite prin distrugere.

Procentul (`procent_limită`) trebuie stabilit din anexele HG 831/2004, pe grupa exactă de alimente — o grupă greșită schimbă rezultatul întregului calcul.

## Ce se greșește în practică

- Se aplică formula la stocul final de alimente, nu la valoarea intrărilor din perioadă.
- Se folosește un singur procent pentru toate categoriile de alimente, deși grupele au coeficienți diferiți.
- Se confundă alimentele cumpărate ca marfă (comercializare) cu ingredientele consumate în prepararea culinară — acestea din urmă țin de pierderi tehnologice (art. 25 alin. (3) lit. e)), cu alt temei și fără coeficient HG 831/2004.
- Se rotunjește manual, în loc să se lase calculul pe zecimale exacte, ceea ce poate produce mici diferențe la partea nedeductibilă și la ajustarea de TVA.

## Ce face iConta.eu

Funcția `calcul` din `core/perisabilitati.py` aplică exact această formulă, cu rotunjire `Decimal`/`ROUND_HALF_UP`, și generează liniile contabile corespunzătoare (607 pe partea deductibilă și, dacă e cazul, pe analiticul nedeductibil, plus 635=4426 pe ajustarea de TVA). Procentul de limită e introdus manual de contabil — aplicația nu conține coeficienții din anexele HG 831/2004 pe grupe de alimente, care trebuie verificați direct în hotărâre.

[iConta.eu](/)
