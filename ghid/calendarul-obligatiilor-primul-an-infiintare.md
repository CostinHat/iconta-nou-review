---
title: "Calendarul obligațiilor în primul an de la înființare"
description: "Termenele legale ale primelor obligații ale unui SRL nou-înființat: înmatricularea, plafonul de TVA și declararea modificărilor la organul fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Calendarul obligațiilor în primul an de la înființare

Precizare de la început: „calendarul obligațiilor din primul an" nu există ca atare într-un singur act normativ — e o compilație de termene diferite, fiecare cu sursa lui proprie (Legea societăților, Codul fiscal, Codul de procedură fiscală). Mai jos sunt termenele pentru care există un temei verificat; pentru orice obligație specifică domeniului de activitate (autorizații sectoriale, licențe), verificarea se face separat, pe legislația aplicabilă acelui domeniu.

## Temeiul legal

::: ghid-temei
„Articolul 36
(1) În termen de 15 zile de la data încheierii actului constitutiv, fondatorii, primii administratori sau, dacă este cazul, primii membri ai directoratului și ai consiliului de supraveghere ori un împuternicit al acestora vor cere înmatricularea societății în registrul comerțului în a cărui rază teritorială își va avea sediul societatea. Ei răspund în mod solidar pentru orice prejudiciu pe care îl cauzează prin neîndeplinirea acestei obligații."
— Legea 31/1990 (Legea societăților), art. 36 alin. (1) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

Primele termene verificabile pentru un SRL nou-înființat:

- **15 zile de la actul constitutiv** — cererea de înmatriculare la registrul comerțului (Legea 31/1990, art. 36 alin. 1). Practic, în majoritatea cazurilor, înmatricularea și înregistrarea fiscală se fac simultan, prin mecanismul de ghișeu unic la ONRC.
- **15 zile de la producerea modificării** — orice schimbare a datelor din declarația de înregistrare fiscală (sediu, administrator, obiect de activitate) trebuie comunicată organului fiscal prin declarație de mențiuni (Legea 207/2015, art. 88 alin. 1) — regulă valabilă tot timpul funcționării firmei, nu doar în primul an.
- **Plafonul de scutire de TVA** — o firmă nou-înființată care nu depășește, în cursul anului calendaristic, plafonul de 395.000 lei nu are obligația să se înregistreze în scopuri de TVA; dacă îl depășește, trebuie să solicite înregistrarea începând cu tranzacția care a condus la depășire (Codul fiscal, art. 310).

Dincolo de acestea, calendarul concret depinde de regimul fiscal ales (micro sau profit), de existența angajaților (caz în care apar obligațiile de declarare D112 lunar) și de obiectul de activitate — nu există un singur termen universal „pentru primul an".

## Ce se greșește în practică

- Se așteaptă un termen fix de tip „30 sau 60 de zile de la înființare" pentru toate obligațiile deodată, deși fiecare obligație are propriul termen și propriul moment de declanșare (unele de la data actului constitutiv, altele de la data primei operațiuni relevante).
- Se ignoră obligația de declarare a modificărilor (sediu, obiect de activitate, administrator) în cele 15 zile de la producerea lor, presupunând că informația „e deja la ONRC, deci ANAF o are automat" — cele două registre nu se sincronizează implicit pentru toate tipurile de modificări.
- Se confundă plafonul de scutire de TVA cu un termen de înregistrare fiscală generală — depășirea plafonului de 395.000 lei declanșează doar obligația de înregistrare în scopuri de TVA, nu afectează celelalte obligații fiscale ale firmei.

## Ce face iConta.eu

iConta.eu are un modul dedicat calendarului de termene ale firmei (`core/termene_api.py`, funcția `termene_firma`), care calculează obligațiile următoare pe baza vectorului fiscal al firmei (regim de TVA, dacă are salariați, ce declarații a depus deja) — util pentru urmărirea obligațiilor curente odată ce firma e configurată în aplicație. Pașii dinaintea acestui punct — înmatricularea la registrul comerțului și prima înregistrare fiscală — au loc în afara aplicației, prin ONRC/ANAF, așa că nu sunt urmăriți automat de iConta.eu; calendarul din aplicație pornește din momentul în care contabilul configurează firma și vectorul ei fiscal.

[iConta.eu](/)
