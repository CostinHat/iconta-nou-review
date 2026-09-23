---
title: Cum corectez CNP-ul asociatului în D205?
description: CNP-ul se corectează în fișa asociatului, nu direct pe declarație — D205 nu are un ecran de completare manuală, se generează automat din datele asociatului. Aplicația respinge la generare orice CNP invalid sau duplicat.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez CNP-ul asociatului în D205?

D205 nu are un ecran separat de completare — CNP-ul fiecărui beneficiar e preluat direct din fișa asociatului la generare. Corecția se face deci la sursă, nu pe formular.

## Temeiul legal

::: ghid-temei
**Art. 97 alin. (7) din Codul fiscal**: „[...] Obligația calculării și reținerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor [...]" — identificarea corectă a fiecărui beneficiar e parte din această obligație de declarare corectă.
:::

## Cum se corectează, în funcție de moment

**Înainte de generarea/depunerea declarației**: corectați CNP-ul direct în fișa asociatului (datele de identificare ale acestuia). La următoarea generare a D205, aplicația preia automat CNP-ul actualizat.

**După depunerea declarației la ANAF, cu CNP greșit**: aplicația nu generează în acest moment o D205 rectificativă (indicatorul dedicat din structura formularului e fixat intern pe „nu e rectificativă") — corectarea unei declarații deja depuse trebuie făcută prin mijloacele oficiale ale ANAF.

## Validările pe care le rulează aplicația

CNP-ul fiecărui beneficiar e verificat pe cifră de control (checksum), nu doar pe „câmp completat" — un CNP invalid nu trece de validare. Rezidența beneficiarului se derivă automat din CNP (prima cifră 1–8 = rezident); un beneficiar fără CNP românesc valid e respins direct la generare, pentru că dividendele către nerezidenți nu se declară pe D205, ci pe D207. În plus, aceeași combinație tip de venit + CNP nu poate apărea de două ori — un CNP duplicat e blocat explicit.

## Ce se greșește în practică

Se încearcă „forțarea" unui CNP care nu trece validarea de cifră de control, presupunând că eroarea e a aplicației — de cele mai multe ori CNP-ul din fișa asociatului e pur și simplu greșit introdus și trebuie verificat cifră cu cifră.

## Ce face iConta.eu

Aplicația validează CNP-ul pe checksum la fiecare generare și blochează atât CNP-urile invalide, cât și duplicatele pe aceeași combinație tip de venit + CNP. Corectarea propriu-zisă a CNP-ului rămâne un pas manual, în fișa asociatului — aplicația nu oferă o funcție de „editare directă" a unei declarații deja generate.

[iConta.eu](/)
