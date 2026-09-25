---
title: "Ghișeul unic IOSS pentru colete mici: cum funcționează"
description: "Regimul special de import IOSS pentru vânzarea la distanță de bunuri din afara UE, cu valoare sub 150 euro, și declarația D399 aferentă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ghișeul unic IOSS pentru colete mici: cum funcționează

IOSS (Import One Stop Shop) este regimul special de TVA pentru vânzarea la distanță către clienți din UE a unor bunuri importate din afara UE, în loturi cu o valoare intrinsecă de maximum 150 euro. Prin acest regim, TVA-ul se colectează o singură dată, la vânzare, și se declară centralizat printr-un singur stat membru de identificare, în loc ca fiecare colet să fie taxat separat la vamă în fiecare stat de destinație.

## Temeiul legal

::: ghid-temei
„În sensul prezentului articol vânzarea la distanță de bunuri importate din teritorii terțe sau țări terțe acoperă numai bunurile, cu excepția produselor care fac obiectul accizelor, în loturi cu o valoare intrinsecă de maximum 150 euro."
— Legea 227/2015, art. 315^2 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Cum funcționează mecanismul, pe scurt:

- **Se aplică doar loturilor cu valoare intrinsecă de maximum 150 euro**, provenite din import din afara UE, altele decât produsele accizabile — peste acest prag, regimul obișnuit de import și TVA la vamă rămâne aplicabil.
- **TVA-ul se colectează la vânzare**, la cota din statul membru al clientului final, nu la vamă — clientul plătește prețul final cu TVA inclus, iar la import coletul nu mai e taxat separat.
- **Declararea se face centralizat**, printr-un singur stat membru de identificare (pentru o firmă din România, ANAF), prin declarația specială de TVA pentru regimul de import.
- **Platformele care facilitează vânzarea** (marketplace-uri online) pot fi ele însele considerate, prin ficțiune legală, ca fiind cele care au primit și livrat bunurile, preluând astfel obligația de colectare a TVA.
- Regimul e opțional — un operator poate alege să nu folosească IOSS, caz în care bunurile importate sub 150 euro urmează regimul obișnuit de TVA la import.

## Ce se greșește în practică

- Se aplică regimul IOSS pentru loturi care depășesc 150 euro valoare intrinsecă, confundând acest prag cu alte plafoane de scutire vamală care nu mai sunt de actualitate.
- Se confundă IOSS (regim de import, pentru bunuri din afara UE) cu OSS (regim pentru vânzări la distanță intracomunitare, între state membre UE) — cele două regimuri au declarații și condiții diferite.
- Nu se urmărește separat, pe stat de consum, TVA-ul colectat prin platformă versus TVA-ul colectat direct de vânzător, ceea ce duce la raportări incomplete în declarația specială.

## Ce face iConta.eu

iConta.eu generează declarația D399 — Declarația specială de TVA pentru regimul special de import (IOSS), potrivit Legii 33/2024 (`core/d399.py`). Declarația calculează structura pe linii de operațiuni și stat membru de consum, dar, așa cum e documentat explicit în cod, **„D399 (IOSS) declară vânzări la distanță pe stat de consum, care aplicația nu le ține pe schema" internă a firmei** — la data acestui ghid, valorile pe stat de consum și cota aplicabilă în fiecare stat **se introduc manual**, prin datele furnizate de contribuabil, aplicația neurmărind automat, pe fiecare vânzare, țara clientului final și cota locală de TVA aplicabilă.

[iConta.eu](/)
