---
title: "Cum corectez CASS declarată greșit în D212?"
description: "CASS se recalculează pe baza plafonată corect (6, 12, 24 sau 72 de salarii minime brute, în funcție de an și de tipul veniturilor) și se corectează prin declarație rectificativă."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez CASS declarată greșit în D212?

Spre deosebire de CAS, care se plafonează în trepte fixe, CASS pentru activități independente și drepturi de proprietate intelectuală se calculează liniar între praguri — o distincție care generează frecvent erori de bază atunci când cineva aplică din reflex logica de la CAS.

## Temeiul legal

::: ghid-temei
„Persoanele fizice care în anul fiscal pentru care se depune declarația [...] au realizat venituri din cele prevăzute la art. 155 alin. (1) lit. b), din una sau mai multe surse, datorează contribuția de asigurări sociale de sănătate la o bază anuală de calcul egală cu suma rezultată prin cumularea venitului net anual realizat/brut sau normei anuale de venit [...] care nu poate fi mai mare decât cea corespunzătoare unei baze anuale de calcul egale cu nivelul de 72 de salarii minime brute pe țară."
— Codul fiscal (Legea 227/2015), art. 170 alin. (1) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt, astfel cum a fost modificat de Legea 239/2025 art. XII pct. 19, aplicabil veniturilor din 2026)
:::

Ce contează la recalculare:

- Pentru veniturile din activități independente și proprietate intelectuală (art. 155 alin. (1) lit. b)), baza de calcul CASS e chiar venitul net realizat, fără plafonare pe trepte — plafonul de 72 de salarii minime brute (începând cu veniturile 2026; anterior 60) e doar un maxim, nu o treaptă fixă.
- Pentru celelalte categorii de venit (chirii, dobânzi, dividende, activități agricole — art. 155 alin. (1) lit. c)-h)), baza de calcul CASS urmează trepte fixe: 6, 12 sau 24 de salarii minime brute (art. 170 alin. (3)), la fel ca la CAS.
- O eroare tipică e aplicarea tratamentului pe trepte (fix la 6/12/24 sm) unor venituri din activități independente, care ar trebui calculate liniar, direct pe venitul net.
- Corectarea se face tot prin declarație rectificativă, depusă în termenul de prescripție (art. 105 din Legea 207/2015).

## Ce se greșește în practică

- Se aplică regula pe trepte (6/12/24 salarii minime, ca la venituri pasive) unor venituri din activități independente, care se calculează liniar pe venitul net efectiv, fără trepte intermediare.
- Se folosește plafonul de 60 de salarii minime brute (valabil pentru veniturile din 2025) pentru declarații privind veniturile din 2026, unde plafonul urcă la 72 de salarii minime brute, conform Legii 239/2025.
- Se omite cumularea CASS din mai multe surse de venit pasiv la încadrarea în treapta de 6, 12 sau 24 de salarii minime.

## Ce face iConta.eu

Motorul `core/d212_engine.py` implementează exact distincția dintre calculul liniar pentru activități independente (`calculeaza_cass`) și tratamentul pe trepte al veniturilor pasive, cu plafonul de 72 de salarii minime brute aplicat corect doar veniturilor din 2026 (`plafoane_an`, care citește Legea 239/2025 art. XII pct. 19), respectiv 60 de salarii minime pentru veniturile din 2025. Calculul e disponibil prin `fisa_d212` numai pentru anii verificați la sursă (2025, 2026) și doar pentru veniturile din activități independente evidențiate în Registrul-jurnal de încasări și plăți.

Pentru veniturile pasive (chirii, dividende, dobânzi, activități agricole), care se calculează pe trepte, aplicația nu are un modul dedicat — recalcularea și corectarea rămân manuale.

[iConta.eu](/)
