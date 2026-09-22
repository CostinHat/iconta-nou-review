---
title: Cum se aplică plafonul de 12 salarii minime la contribuții?
description: CAS devine obligatorie doar dacă venitul net anual din activități independente atinge 12 salarii minime brute pe țară, cu bază de calcul în trepte — 12 salarii minime între 12 și 24 de salarii, respectiv 24 de salarii minime peste acest nivel.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se aplică plafonul de 12 salarii minime la contribuții?

Plafonul de 12 salarii minime este pragul care decide dacă un PFA în sistem real datorează contribuția de asigurări sociale (CAS — pensii). Sub acest prag, plata CAS este opțională; peste el, devine obligatorie, iar baza de calcul urcă în trepte, nu proporțional cu venitul realizat.

## Temeiul legal

::: ghid-temei
**Art. 148 alin.(1):** "Persoanele fizice care în anul fiscal ... au realizat venituri din activitățile prevăzute la art. 137 alin. (1) lit. b) și b^1) ... a căror valoare anuală cumulată este cel puțin egală cu 12 salarii minime brute pe țară, datorează contribuția de asigurări sociale la o bază de calcul stabilită potrivit alin. (2)."

**Art. 148 alin.(2):** "a) nivelul de 12 salarii minime brute pe țară, în cazul veniturilor realizate cuprinse între 12 salarii minime brute pe țară inclusiv și 24 de salarii minime brute pe țară; b) nivelul de 24 de salarii minime brute pe țară, în cazul veniturilor realizate cel puțin egale cu 24 de salarii minime brute pe țară."

**Art. 148 alin.(4):** "Persoanele fizice ... care nu se încadrează în plafonul de cel puțin 12 salarii prevăzut la alin. (3) pot opta pentru plata contribuției de asigurări sociale...".

**Art. 138 lit.a):** "25% datorată de către persoanele fizice care au calitatea de angajați sau pentru care există obligația plății contribuției de asigurări sociale".
:::

## Trei zone, nu o singură formulă

Cu salariul minim de 4.050 lei (valabil pentru veniturile din 2025 și 2026), plafoanele sunt: (în practică se raportează la salariul minim valabil la 1 ianuarie al anului de venit, fixat pentru tot anul — acest reper nu e menționat explicit în textul art. 148, așa că e prudent să fie tratat ca practică uzuală, nu ca literă de lege directă)

- **Sub 48.600 lei** (12 salarii minime) — CAS neobligatorie; poate fi plătită opțional, caz în care baza tot sare la 48.600 lei, nu la venitul real.
- **Între 48.600 și 97.200 lei** (12–24 salarii minime) — CAS obligatorie, dar baza de calcul e fixă la 48.600 lei, indiferent dacă venitul e 50.000 sau 90.000 lei.
- **Peste 97.200 lei** (24 salarii minime) — CAS obligatorie, bază plafonată la 97.200 lei, chiar dacă venitul e mult mai mare.

::: ghid-exemplu
Un PFA cu venit net de 70.000 lei în 2025 se încadrează în treapta 12–24 salarii minime. CAS se calculează la baza de 48.600 lei (nu la 70.000 lei): 48.600 × 25% = 12.150 lei CAS datorată, nu 70.000 × 25%.
:::

## Ce se greșește în practică

- Se calculează CAS ca procent din venitul net efectiv, ignorând că baza e plafonată în trepte fixe de 12 sau 24 de salarii minime.
- Se folosește salariul minim de la data declarării (de exemplu cel majorat de la 1 iulie), în loc de cel valabil la 1 ianuarie al anului de venit — în practică reperul folosit e fix pe tot anul, deși acest detaliu nu rezultă explicit din textul art. 148, așa că merită confirmat cu prudență, nu tratat ca regulă legală certă.
- Se uită că, dacă PFA cumulează mai multe surse de venit din activități independente (mai multe PFA-uri, contracte sportive), plafonul de 12/24 salarii minime se verifică pe suma cumulată a tuturor acestor venituri, nu doar pe venitul unui singur PFA.
- Se aplică opțional CAS la un venit sub 12 salarii minime fără să se înțeleagă că baza de calcul optată tot devine 12 salarii minime, nu venitul real.

## Ce face iConta.eu

`core/d212_engine.py`, funcția `calculeaza_cas`, implementează exact această structură pe trepte: sub 12 salarii minime, CAS e opțională (dacă se bifează opțiunea, baza devine 12 salarii minime); între 12 și 24 de salarii minime, baza e fixă la 12 salarii minime; peste 24 de salarii minime, baza e plafonată la 24 de salarii minime. Cota aplicată e 25%, conform art. 138 lit. a). Acest comportament e confirmat de dosarul de temei legal ca fiind conform art. 148 — spre deosebire de CASS, aici nu există nicio discrepanță identificată între cod și lege. Un singur aspect nu e modelat automat: dacă venitul PFA se cumulează cu alte surse de venit independent la același plafon (art. 148 alin. (3)), verificarea cumulului rămâne responsabilitatea contabilului.

[iConta.eu](/)
