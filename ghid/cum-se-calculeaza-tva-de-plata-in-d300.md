---
title: Cum se calculează TVA de plată în D300?
description: TVA de plată rezultă din diferența dintre total taxă colectată și total taxă dedusă, cumulată cu soldul de plată reportat din luna precedentă — sold pe care contabilul trebuie să-l introducă manual la fiecare depunere.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează TVA de plată în D300?

Suma de plată din decontul de TVA nu e pur și simplu „colectat minus deductibil” — e rezultatul unui lanț de regularizări care include și soldurile reportate din luna anterioară. Înțelegerea acestui lanț e importantă pentru că una dintre componente nu se completează automat.

## Temeiul legal

::: ghid-temei
„36 Suma negativă a TVA în perioada de raportare (rd. 35 - rd. 19)
37 Taxa de plată în perioada de raportare (rd. 19 - rd. 35)
38 Soldul TVA de plată din decontul perioadei fiscale precedente (rd. 44 din decontul
   perioadei fiscale precedente) neachitate până la data depunerii decontului de TVA
39 Diferenţe de TVA de plată stabilite de organele fiscale [...]
40 TVA de plată cumulat (rd. 37 + rd. 38 + rd. 39)
41 Soldul sumei negative a TVA reportate din perioada precedentă pentru care nu s-a
   solicitat rambursare (rd. 45 din decontul perioadei fiscale precedente)
42 Diferenţe negative de TVA stabilite de organele de inspecţie fiscală [...]
43 Suma negativă a TVA cumulate (rd. 36 + rd. 41 + rd. 42)
44 Sold TVA de plată la sfârşitul perioadei de raportare (rd. 40 - rd. 43)
45 Soldul sumei negative de TVA la sfârşitul perioadei de raportare (rd. 43-rd. 40)”
— OPANAF 174/2026, ANEXA 2, secțiunea „Regularizări conform art.303 din Codul fiscal”

„Rândul 38 - se preia suma prevăzută la rândul 44 din decontul perioadei precedente celei de
raportare, din care se scad sumele achitate până la data depunerii decontului.”
— OPANAF 174/2026, instrucțiuni rd.38
:::

## Lanțul de calcul, pas cu pas

Totul pornește de la rd.19 (TOTAL TAXĂ COLECTATĂ) și rd.35 (TOTAL TAXĂ DEDUSĂ). Din diferența lor rezultă fie o taxă de plată pe perioada curentă (rd.37), fie o sumă negativă pe perioada curentă (rd.36) — niciodată amândouă.

Taxa de plată cumulată (rd.40) adaugă la rd.37 soldul de plată neachitat reportat din luna precedentă (rd.38) și eventualele diferențe stabilite de organele fiscale (rd.39). Suma efectiv de plată la sfârșitul perioadei (rd.44) e diferența dintre acest cumulat și suma negativă cumulată (rd.43).

::: ghid-exemplu
Firmă cu TVA colectată 24.000 lei (rd.19) și TVA dedusă 19.000 lei (rd.35) în luna curentă, fără sold reportat din luna precedentă:
- rd.37 (taxă de plată perioada curentă) = 24.000 − 19.000 = 5.000 lei
- rd.38 (sold reportat) = 0
- rd.40 (TVA de plată cumulat) = 5.000 + 0 + 0 = 5.000 lei
- rd.44 (sold de plată la sfârșitul perioadei) = 5.000 lei, de achitat până pe 25 ale lunii următoare.
:::

## Ce se greșește în practică

- Confuzia dintre rd.37 (taxa de plată doar pe luna curentă) și rd.44 (soldul final, cumulat cu reportul) — se declară sau se plătește suma greșită.
- Omiterea soldului reportat din luna precedentă (rd.38) — dacă a rămas o sumă de plată neachitată din decontul anterior, ea trebuie adunată, nu ignorată.
- Presupunerea că 9% deductibil pe achiziții se calculează automat exact ca 21%/11% — cota de 9% deductibilă nu se emite automat, ci doar se semnalează, tocmai pentru că validarea ANAF o respinge dacă apare fără justificare corectă.
- Introducerea manuală a soldului reportat cu o cifră transcrisă greșit din decontul lunii anterioare — sursă frecventă de erori pentru că nu există preluare automată.

## Ce face iConta.eu

Lanțul de la rd.36 la rd.45 e calculat automat, cu formule identice cu cele din OPANAF 174/2026 (codul intern folosește denumirile de atribut R33–R42 pentru aceleași rânduri tipărite 36–45). Ce NU se preia automat: soldul de plată reportat (rd.38) și soldul sumei negative reportat fără rambursare cerută (rd.41) sunt câmpuri complet manuale — contabilul trebuie să le introducă la fiecare depunere, pe baza rd.44/rd.45 din decontul lunii precedente. TVA deductibilă la cota de 9% nu se auto-emite din facturi — apare doar ca avertisment, tocmai pentru că validatorul ANAF o respinge fără o justificare introdusă corect.

[iConta.eu](/)
