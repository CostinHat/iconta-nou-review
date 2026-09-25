---
title: "Cum se calculează CASS pentru PFA în 2026?"
description: "Pentru veniturile din 2026, CASS se calculează liniar (10%) pe venitul net, plafonat la 72 de salarii minime brute pe țară — plafon urcat de la 60, prin Legea 239/2025."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează CASS pentru PFA în 2026?

Regula de calcul rămâne aceeași ca în anii anteriori — cota de 10% aplicată liniar pe venitul net — dar plafonul maxim se schimbă începând cu veniturile din 2026, printr-o modificare legislativă de la finalul lui 2025.

## Temeiul legal

::: ghid-temei
„Persoanele fizice care în anul fiscal pentru care se depune declarația [...] au realizat venituri din cele prevăzute la art. 155 alin. (1) lit. b), din una sau mai multe surse, datorează contribuția de asigurări sociale de sănătate la o bază anuală de calcul egală cu suma rezultată prin cumularea venitului net anual realizat/brut sau normei anuale de venit, respectiv a normei anuale de venit ajustate, după caz [...] care nu poate fi mai mare decât cea corespunzătoare unei baze anuale de calcul egale cu nivelul de 72 de salarii minime brute pe țară."
— Codul fiscal (Legea 227/2015), art. 170 alin. (1), astfel cum a fost modificat de Legea 239/2025 art. XII pct. 19, aplicabil veniturilor din 2026 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Pașii de calcul pentru veniturile 2026:

- Se cumulează venitul net anual (sau norma anuală de venit, ajustată, dacă e cazul) din toate sursele de activități independente și drepturi de proprietate intelectuală ale contribuabilului.
- Se aplică cota de 10% (art. 156) pe acest venit cumulat, fără trepte intermediare — spre deosebire de CAS, care se plafonează în trepte, CASS pentru aceste venituri e liniară.
- Plafonul maxim al bazei de calcul e 72 de salarii minime brute pe țară pentru veniturile din 2026 — anterior, pentru veniturile din 2025, plafonul era 60 de salarii minime brute.
- Reperul de salariu minim folosit e cel în vigoare la 1 ianuarie a anului de realizare a venitului, fix pe tot anul — o eventuală majorare ulterioară (de exemplu în iulie) nu modifică reperul deja stabilit.

## Ce se greșește în practică

- Se aplică plafonul vechi de 60 de salarii minime brute pentru veniturile din 2026, ignorând majorarea la 72 de salarii minime brute adusă de Legea 239/2025.
- Se calculează CASS pe salariul minim majorat de la 1 iulie, în loc de reperul fix de la 1 ianuarie al anului de venit.
- Se aplică regula pe trepte (specifică veniturilor pasive) în loc de calculul liniar, specific veniturilor din activități independente.

## Ce face iConta.eu

Motorul `core/d212_engine.py` implementează exact această distincție pentru anul de venit 2026: funcția `plafoane_an(2026)` ridică pragul maxim la 72 de salarii minime brute, citind Legea 239/2025 art. XII pct. 19, verificată la sursă, în timp ce reperul de salariu minim rămâne fix la valoarea de la 1 ianuarie 2026 (4.050 lei, conform HG 1506/2024), indiferent de majorarea ulterioară din iulie 2026. Calculul liniar al CASS (`calculeaza_cass`) e disponibil prin `fisa_d212` (`core/rip_api.py`), pentru contribuabilii cu evidență în Registrul-jurnal de încasări și plăți.

Aplicația refuză explicit calculul pentru orice an fiscal în afara celor verificate la sursă (2025, 2026) — un an neverificat ar produce o fișă plauzibilă, dar pe praguri neconfirmate.

[iConta.eu](/)
