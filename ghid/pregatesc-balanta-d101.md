---
title: Cum pregătesc balanța pentru D101
description: Ce condiții minime trebuie îndeplinite în balanță și în datele firmei înainte ca D101 să poată fi generată, conform validărilor din motorul de calcul.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum pregătesc balanța pentru D101

Înainte de a genera D101, aplicația verifică o serie de condiții minime — atât la nivel de date de identificare, cât și la nivel de balanță. Dacă lipsește ceva esențial, declarația pur și simplu nu se generează.

## Temeiul legal

::: ghid-temei
„D101 nu se poate genera fără CUI valid (checksum verificat prin `core.identitate.valideaza_cui`), denumire, adresă, cod CAEN pe 4 cifre; plus erorile de declarant din `core.firma_profil_api.erori_declarant`."
— sursă: `core/d101.py`, funcția `erori_generare`, liniile 366–388, dosar de cercetare F027.

D101 „citește profilul firmei + balanța, cu split exploatare/financiar (clasele 76/66 = financiar, restul 7x/6x = exploatare) și datele pentru rezerva legală (capital 1012, rezervă existentă 1061, cheltuială impozit 691)"
— sursă: `core/d101.py`, funcția `pull()`, liniile 448–467, dosar de cercetare F027.
:::

Pregătirea balanței pentru D101 înseamnă, concret, verificarea a două seturi de lucruri:

1. **Date de identificare a firmei**: CUI valid (cu checksum verificat), denumire, adresă și cod CAEN complet, pe 4 cifre. Fără acestea, declarația nu se generează deloc.
2. **Solduri de balanță corect încheiate**: contul 1012 (capital social), 1061 (rezervă legală existentă), 691 (cheltuiala cu impozitul pe profit), plus separarea corectă a claselor 76/66 (financiar) de restul claselor 7x/6x (exploatare).

## Ce se greșește în practică

Greșeala tipică e generarea declarației înainte de închiderea completă a lunii/anului contabil, când balanța încă are conturi tranzitorii nedecontate (mai ales 691 și conturile de venituri/cheltuieli financiare). A doua greșeală este un cod CAEN incomplet sau vechi (mai puțin de 4 cifre, sau neactualizat) în profilul firmei, care blochează generarea fără un mesaj imediat evident pentru utilizator.

## Ce face iConta.eu

iConta.eu rulează un set de validări explicite înainte de a permite generarea D101: CUI valid, denumire, adresă, cod CAEN pe 4 cifre, plus verificările de profil declarant. La generare, preia automat din balanță datele necesare pentru rezerva legală și pentru split-ul exploatare/financiar. Dacă cifra de afaceri a anului precedent transmisă depășește pragul IMCA (50.000.000 EUR) și valoarea de la P47 nu a fost introdusă manual, aplicația o cere explicit înainte de generare — pentru a nu subevalua tacit impozitul unei firme mari.

[iConta.eu](/)
