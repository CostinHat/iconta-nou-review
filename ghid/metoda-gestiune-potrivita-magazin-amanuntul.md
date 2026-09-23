---
title: Ce metodă de gestiune este potrivită pentru un magazin cu amănuntul?
description: Când metoda prețului cu amănuntul (global-valorică) e potrivită pentru un magazin de vânzare cu amănuntul, conform OMFP 1802/2014 și mecanismului implementat de iConta.eu.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce metodă de gestiune este potrivită pentru un magazin cu amănuntul?

Legea prevede explicit condițiile în care metoda prețului cu amănuntul (numită în iConta.eu „gestiune global-valorică") este potrivită, iar profilul unui magazin clasic de vânzare cu amănuntul se potrivește, de regulă, exact cu aceste condiții.

## Temeiul legal

::: ghid-temei
„În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă. În această situație, costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor. Orice modificare a prețului de vânzare presupune recalcularea marjei brute."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (8)
:::

Textul stabilește trei criterii pentru care metoda prețului cu amănuntul e potrivită: articole **numeroase**, cu **mișcare rapidă** și cu **marje similare** între ele — situație tipică pentru un magazin de tip retail, unde ar fi impracticabil să se urmărească costul de achiziție individual al fiecărui produs, articol cu articol.

## Ce se greșește în practică

- Se alege metoda global-valorică doar pentru că e „mai simplă", fără să se verifice dacă articolele au marje similare — dacă magazinul vinde categorii cu marje foarte diferite între ele, coeficientul K, calculat agregat, devine puțin relevant pentru fiecare categorie în parte.
- Se schimbă metoda de gestiune de la un exercițiu la altul fără motiv documentat — reglementarea (pct. 287 din același act normativ) cere consecvență în aplicarea metodei între exerciții, iar o schimbare trebuie motivată și prezentată în notele explicative.
- Se combină metoda global-valorică cu inventarul intermitent — cele două nu pot coexista pentru aceleași stocuri (vezi mai jos).

## Ce face iConta.eu

Aplicația implementează metoda prețului cu amănuntul ca funcționalitate de sine stătătoare (gestiune global-valorică): NIR-urile la intrare fixează costul, adaosul și TVA neexigibilă, iar descărcarea lunară calculează costul mărfii vândute prin coeficientul K, exact mecanismul descris de pct. 286 alin. (8). Pentru un magazin de vânzare cu amănuntul cu multe articole și marje relativ similare, această metodă e alegerea potrivită și cea susținută tehnic de această funcționalitate.

Trebuie reținut și aspectul complementar: reglementarea (pct. 291 alin. (5) din același act) interzice explicit folosirea inventarului intermitent în comerțul cu amănuntul atunci când se aplică metoda global-valorică — cele două nu se pot combina.

[iConta.eu](/)
