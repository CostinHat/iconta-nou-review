---
title: Se declară dividendele în D205?
description: Da — dividendele plătite persoanelor fizice se declară în D205, cu tip de venit codificat "08". Dividendele către persoane juridice merg pe D100, iar cele către nerezidenți pe D207.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Se declară dividendele în D205?

Da. Dividendele plătite persoanelor fizice rezidente se declară în D205, sub codul de tip de venit „08" — condiția e ca beneficiarul să fie o persoană fizică identificabilă printr-un CNP românesc valid.

## Temeiul legal

::: ghid-temei
**Art. 97 alin. (7) din Codul fiscal**: „Veniturile sub formă de dividende [...] se impozitează cu o cotă de 16% din suma acestora, impozitul fiind final. Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...]"
:::

## Ce anume se declară

Formularul D205 folosește codul de tip venit „08" pentru dividende, cu două valori cheie completate pentru fiecare beneficiar: suma distribuită și suma efectiv plătită — sunt tratate separat, pentru că impozitul se calculează pe suma **plătită**, nu pe cea doar distribuită/aprobată.

D205 acoperă exclusiv dividendele plătite persoanelor **fizice**. Dividendele către persoane juridice se raportează separat, prin D100 (poziția cu cod 150, temei art. 43 din Codul fiscal), iar cele către beneficiari nerezidenți, prin D207 — nu prin D205.

## Ce se greșește în practică

Se presupune că un singur formular acoperă toate dividendele plătite de firmă, indiferent de tipul beneficiarului — de fapt, tipul de beneficiar (persoană fizică rezidentă / persoană juridică / nerezident) determină formularul corect, iar D205 e valabilă strict pentru primul caz.

## Ce face iConta.eu

D205 se generează automat cu tip de venit „08" pentru orice sumă de dividend identificată pe contul 457, împărțită între asociați conform cotelor lor de participare. Un beneficiar fără CNP românesc valid e respins direct la generare — aplicația nu permite includerea lui greșită pe D205; dividendele către nerezidenți trebuie tratate separat, prin D207.

[iConta.eu](/)
