---
title: Lipsurile în limitele normelor de perisabilitate
description: Pierderea încadrată în limita coeficientului de perisabilitate aplicat la valoarea intrărilor e deductibilă integral, fără ajustare de TVA — dar procentul aplicabil grupei de mărfuri se stabilește din anexele HG 831/2004, nu se calculează automat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Lipsurile în limitele normelor de perisabilitate

Când pierderea constatată la o marfă se încadrează în limita coeficientului de perisabilitate stabilit pentru grupa ei, tratamentul fiscal e simplu: cheltuiala e deductibilă integral, fără nicio ajustare de TVA. Complicația apare la stabilirea limitei — procentul aplicabil ține de anexele HG 831/2004, pe grupe de mărfuri, nu e o valoare fixă valabilă pentru toate produsele.

## Temeiul legal

::: ghid-temei
„Se aprobă Normele privind limitele admisibile de perisabilitate la mărfuri în procesul de comercializare, prevăzute în anexa care face parte integrantă din prezenta hotărâre."

*(HG nr. 831/2004 pentru aprobarea Normelor privind limitele admisibile de perisabilitate la mărfuri în procesul de comercializare, art. 1)*
:::

## Cum se calculează „în limită"

Limita maximă deductibilă se aplică la **prețul de înregistrare al produselor intrate**, nu la valoarea produsului constatat lipsă și nici la stocul final:

`limita = valoare_intrări × procent_limită / 100`

Dacă pierderea constatată e mai mică sau egală cu limita astfel calculată, întreaga pierdere e deductibilă (607, pe cont de stoc), fără nicio ajustare de TVA — condiție necesară, dar nu automat îndeplinită doar prin calcul: se cer și verificare faptică (inventariere, recepție sau predare de gestiune), aprobarea administratorului și proces-verbal.

## Ce nu sunt perisabilități

Nu orice pierdere de marfă intră sub acest regim. Sunt excluse explicit: consumul tehnologic, neglijența, sustragerile și forța majoră — situații care au propriile regimuri fiscale, distincte de perisabilitatea de comercializare.

## Ce se greșește în practică

- Se calculează limita la valoarea stocului final sau la valoarea lipsei constatate, în loc de valoarea intrărilor din perioadă.
- Se aplică un procent „standard" fără verificare în anexele HG 831/2004, pentru grupa de mărfuri corectă.
- Se omit condițiile documentare (verificare faptică, aprobarea administratorului, proces-verbal), deși pierderea s-ar fi încadrat valoric în limită.
- Se confundă perisabilitatea (marfă în procesul de comercializare) cu pierderea tehnologică din producție/preparare, care are alt temei legal (art. 25 alin. (3) lit. e)).

## Ce face iConta.eu

Motorul F066 (`core/perisabilitati.py`) calculează automat `limita`, separă deductibilul de nedeductibil (`deductibil = min(pierdere_constatată, limita)`) și nu aplică nicio ajustare de TVA cât timp toată pierderea se încadrează în limită. Procentul de limită (`procent_limita`) se introduce manual de contabil — aplicația nu conține tabelul coeficienților pe grupe de mărfuri din anexele HG 831/2004; procentul aplicabil grupei de produse trebuie verificat direct în anexa hotărârii, publicată în Monitorul Oficial.

[iConta.eu](/)
