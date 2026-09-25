---
title: "Care este baza de calcul pentru CASS la PFA în 2026?"
description: "Baza CASS pentru 2026 e venitul net cumulat din activități independente, fără trepte intermediare, plafonat la 72 de salarii minime brute pe țară (291.600 lei, la reperul de 4.050 lei)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Care este baza de calcul pentru CASS la PFA în 2026?

Baza de calcul pentru CASS nu e o simplă valoare aleasă de contribuabil, ca la CAS — e chiar venitul net cumulat, într-un interval liniar între un prag minim opțional și un plafon maxim obligatoriu.

## Temeiul legal

::: ghid-temei
„Persoanele fizice care în anul fiscal pentru care se depune declarația [...] au realizat venituri din cele prevăzute la art. 155 alin. (1) lit. b), din una sau mai multe surse, datorează contribuția de asigurări sociale de sănătate la o bază anuală de calcul egală cu suma rezultată prin cumularea venitului net anual realizat/brut sau normei anuale de venit, respectiv a normei anuale de venit ajustate, după caz, stabilite potrivit art. 68, 68^1, 68^3 și 69, după caz, care nu poate fi mai mare decât cea corespunzătoare unei baze anuale de calcul egale cu nivelul de 72 de salarii minime brute pe țară."
— Codul fiscal (Legea 227/2015), art. 170 alin. (1), astfel cum a fost modificat de Legea 239/2025 art. XII pct. 19, aplicabil veniturilor din 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce compune concret baza, pentru veniturile din 2026:

- Punctul de plecare e venitul net anual (sistem real, art. 68), norma anuală de venit ajustată (art. 69) sau venitul din drepturi de activitate sportivă/proprietate intelectuală (art. 68^1, 68^3), cumulate dacă provin din mai multe surse.
- La determinarea bazei nu se iau în calcul pierderile fiscale anuale (art. 170 alin. (1), teza finală) — o pierdere la o altă categorie de venit nu reduce baza CASS.
- Plafonul maxim e 72 de salarii minime brute pe țară pentru veniturile din 2026 — la reperul de 4.050 lei (salariul minim de la 1 ianuarie 2026), asta înseamnă o bază maximă de 291.600 lei.
- Sub pragul minim de 6 salarii minime brute (24.300 lei, la același reper), CASS nu e obligatorie, dar contribuabilul poate opta pentru plata ei (art. 180).

## Ce se greșește în practică

- Se calculează plafonul pe salariul minim majorat pe parcursul anului (de exemplu, cel din iulie), în loc de reperul fix de la 1 ianuarie al anului de venit.
- Se scad pierderi fiscale din baza CASS, deși legea exclude explicit această operațiune.
- Se ignoră cumularea veniturilor din mai multe surse de activități independente la stabilirea bazei — fiecare sursă tratată separat poate rămâne sub plafon, deși cumulat baza îl depășește.

## Ce face iConta.eu

Motorul `core/d212_engine.py` calculează baza CASS conform acestei formule pentru veniturile din 2026: liniar pe venitul net, cu prag minim opțional de 6 salarii minime brute și plafon maxim de 72 de salarii minime brute (291.600 lei, la reperul de 4.050 lei verificat la sursă din registrul de cote al aplicației). Calculul e disponibil prin `fisa_d212` (`core/rip_api.py`), pentru contribuabilii cu evidență în Registrul-jurnal de încasări și plăți ținută în aplicație.

Aplicația nu cumulează automat baza CASS din surse de venit aflate în afara Registrului-jurnal de încasări și plăți (de exemplu, drepturi de proprietate intelectuală declarate separat) — cumularea manuală a tuturor surselor rămâne responsabilitatea contabilului.

[iConta.eu](/)
