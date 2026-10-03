---
title: "Care este baza de calcul pentru CASS la PFA în 2026?"
description: "Baza CASS pentru 2026 e venitul net cumulat din activități independente, fără trepte intermediare, plafonat la 72 de salarii minime brute pe țară (291.600 lei, la reperul de 4.050 lei)."
published: 2026-09-26
modified: 2026-10-03
poarta: v1
---

# Care este baza de calcul pentru CASS la PFA în 2026?

Baza de calcul pentru CASS nu e o simplă valoare aleasă de contribuabil, ca la CAS — e chiar venitul net cumulat, între o bază minimă de 6 salarii minime și un plafon maxim de 72 de salarii minime.

## Temeiul legal

::: ghid-temei
„Persoanele fizice care în anul fiscal pentru care se depune declarația [...] au realizat venituri din cele prevăzute la art. 155 alin. (1) lit. b), din una sau mai multe surse, datorează contribuția de asigurări sociale de sănătate la o bază anuală de calcul egală cu suma rezultată prin cumularea venitului net anual realizat/brut sau normei anuale de venit, respectiv a normei anuale de venit ajustate, după caz, stabilite potrivit art. 68, 68^1, 68^3 și 69, după caz, care nu poate fi mai mare decât cea corespunzătoare unei baze anuale de calcul egale cu nivelul de 72 de salarii minime brute pe țară."
— Codul fiscal (Legea 227/2015), art. 170 alin. (1), astfel cum a fost modificat de Legea 239/2025 art. XII pct. 19, aplicabil veniturilor din 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Ce compune concret baza, pentru veniturile din 2026:

- Punctul de plecare e venitul net anual (sistem real, art. 68), norma anuală de venit ajustată (art. 69) sau venitul din drepturi de activitate sportivă/proprietate intelectuală (art. 68^1, 68^3), cumulate dacă provin din mai multe surse.
- La determinarea bazei nu se iau în calcul pierderile fiscale anuale (art. 170 alin. (1), teza finală) — o pierdere la o altă categorie de venit nu reduce baza CASS.
- Plafonul maxim e 72 de salarii minime brute pe țară pentru veniturile din 2026 — la reperul de 4.050 lei (salariul minim de la 1 ianuarie 2026), asta înseamnă o bază maximă de 291.600 lei.
- Sub 6 salarii minime brute (24.300 lei, la același reper), baza urcă la 24.300 lei: art. 174 alin. (6) cere „o diferență de contribuție … până la nivelul celei corespunzătoare bazei de calcul egale cu 6 salarii minime brute pe țară”, afară de excepțiile din art. 174 alin. (7) (salarii sau alte venituri cu CASS de cel puțin 6 salarii minime, pensii). Doar la pierdere sau venit net zero CASS nu se datorează (se poate opta, art. 180).

## Ce se greșește în practică

- Se calculează plafonul pe salariul minim majorat pe parcursul anului (de exemplu, cel din iulie), în loc de reperul fix de la 1 ianuarie al anului de venit.
- Se scad pierderi fiscale din baza CASS, deși legea exclude explicit această operațiune.
- Se ignoră cumularea veniturilor din mai multe surse de activități independente la stabilirea bazei — fiecare sursă tratată separat poate rămâne sub plafon, deși cumulat baza îl depășește.

## Ce face iConta.eu

Motorul `core/d212_engine.py` calculează baza CASS conform acestei formule pentru veniturile din 2026: liniar pe venitul net, cu baza minimă de 6 salarii minime brute (diferența arătată separat, cu varianta pentru excepțiile din art. 174 alin. (7)) și plafon maxim de 72 de salarii minime brute (291.600 lei, la reperul de 4.050 lei verificat la sursă din registrul de cote al aplicației). Calculul e disponibil prin `fisa_d212` (`core/rip_api.py`), pentru contribuabilii cu evidență în Registrul-jurnal de încasări și plăți ținută în aplicație.

Fișa nu cumulează sursele din afara Registrului-jurnal de încasări și plăți; Declarația unică (D212) le cumulează însă, dacă sunt introduse în formular (de exemplu, drepturile de proprietate intelectuală sau o altă activitate independentă), calculând CASS pe fiecare cumul cerut de lege. Ce sursă există, o știe și o introduce contabilul.

[iConta.eu](/)
