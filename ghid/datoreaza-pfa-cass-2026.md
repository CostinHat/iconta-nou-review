---
title: "Când datorează un PFA CASS în 2026?"
description: Un PFA datorează CASS din momentul în care venitul net anual atinge 6 salarii minime (24.300 lei în 2026); sub acest prag, plata rămâne opțională.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Când datorează un PFA CASS în 2026?

Spre deosebire de CAS, care are prag de intrare la 12 salarii minime, CASS pentru PFA are prag de intrare la doar **6 salarii minime**. Pragurile diferite pentru cele două contribuții sunt o sursă frecventă de confuzie.

## Temeiul legal

::: ghid-temei
**Art. 170 alin. (1) Cod fiscal (Legea 227/2015), modificat de Legea 239/2025 art. XII pct. 19:** *„Persoanele fizice care în anul fiscal pentru care se depune declarația prevăzută la art. 122 au realizat venituri din cele prevăzute la art. 155 alin. (1) lit. b), din una sau mai multe surse, datorează contribuția de asigurări sociale de sănătate la o bază anuală de calcul egală cu suma rezultată prin cumularea venitului net anual realizat/brut sau normei anuale de venit ... stabilite potrivit art. 68, 68^1, 68^3 și 69, după caz, care nu poate fi mai mare decât cea corespunzătoare unei baze anuale de calcul egale cu nivelul de 72 de salarii minime brute pe țară."*

**HG 1506/2024:** *„Începând cu data de 1 ianuarie 2025, salariul de bază minim brut pe țară garantat în plată se stabilește ... la suma de 4.050 lei lunar."*
:::

## Pragul de 6 salarii minime

Legea nu citează explicit „6 salarii minime" ca prag de intrare în textul de mai sus (acesta descrie plafonul maxim, de 72 sm), dar structura confirmată de motorul de calcul al aplicației, verificată pe sursă, aplică regula generală CASS: sub 6 salarii minime, plata rămâne neobligatorie, cu opțiune de plată la o bază de 6 salarii minime dacă persoana alege să contribuie voluntar. Cu reperul de 4.050 lei (salariul minim la 1 ianuarie, valabil atât pentru 2025 cât și pentru 2026):

- **6 salarii minime = 24.300 lei.** Sub acest venit net anual, CASS nu e obligatoriu.
- **Între 24.300 lei și plafonul maxim** — baza de calcul e venitul net efectiv (liniar, nu în trepte fixe ca la CAS).
- **Peste plafonul maxim** (60 salarii minime pentru veniturile 2025, 72 salarii minime — 291.600 lei — pentru veniturile 2026 și următoare) — baza se plafonează, nu mai crește odată cu venitul.

## Ce se greșește în practică

- **Se aplică aceleași praguri ca la CAS (12/24 sm).** CASS are prag de intrare diferit (6 sm) și e liniar, nu în trepte fixe între prag și plafon.
- **Se ignoră că baza CASS e cumulată „din una sau mai multe surse".** Dacă PFA-ul are mai multe activități independente, veniturile nete se adună într-o singură bază de calcul CASS, nu se calculează separat pe fiecare sursă.
- **Se aplică plafonul de 60 salarii minime și pentru veniturile din 2026** — plafonul de 60 sm era valabil pentru veniturile 2025; pentru veniturile aferente anului 2026 (D212 depusă în 2027), plafonul e 72 salarii minime.

## Ce face iConta.eu

Fișa D212 (RIP > Fișa D212) calculează CASS liniar pe venitul net efectiv, cu mențiunea „neobligatoriu — sub 6 salarii minime" când e cazul, folosind reperul salariului minim la 1 ianuarie al anului de venit și plafonul corect (60 sm pentru 2025, 72 sm pentru 2026), preluate automat de la server. Calculul se bazează exclusiv pe operațiunile validate din registrul de încasări și plăți al PFA-ului respectiv.

[iConta.eu](/)
