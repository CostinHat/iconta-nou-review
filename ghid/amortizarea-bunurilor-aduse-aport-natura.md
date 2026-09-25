---
title: "Amortizarea bunurilor aduse ca aport în natură la capital"
description: "Valoarea fiscală de la care pornește amortizarea unui mijloc fix adus ca aport în natură la capitalul social, conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amortizarea bunurilor aduse ca aport în natură la capital

Un mijloc fix adus ca aport în natură la capitalul social nu se amortizează pornind de la o valoare aleasă arbitrar — Codul fiscal leagă explicit valoarea fiscală de amortizare de valoarea de piață stabilită la evaluarea aportului.

## Temeiul legal

::: ghid-temei
„costul de achiziție, de producție sau valoarea de piață a mijloacelor fixe dobândite cu titlu gratuit ori constituite ca aport, la data intrării în patrimoniul contribuabilului, utilizată pentru calculul amortizării fiscale, după caz - pentru mijloace fixe amortizabile și terenuri."
— Legea 227/2015 (Codul fiscal), art. 7 pct. 44 lit. c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din definiția valorii fiscale rezultă mecanismul de amortizare pentru un aport în natură:

- Baza de amortizare a unui mijloc fix constituit ca aport este **valoarea de piață stabilită la data intrării în patrimoniu** — practic, valoarea de aport rezultată din evaluarea făcută la constituirea sau majorarea capitalului social, nu o valoare declarată arbitrar de asociat.
- Această regulă corespunde și principiului contabil general: la data intrării în entitate, bunurile reprezentând aport la capitalul social se evaluează „**la valoarea de aport, stabilită în urma evaluării**" (OMFP 1802/2014, pct. 75 alin. (1) lit. c)) — valoarea de aport se substituie costului de achiziție ca bază de pornire.
- Dacă ulterior se efectuează reevaluări ale mijlocului fix care determină o **descreștere** a valorii sub valoarea de piață inițială a aportului, valoarea fiscală rămasă neamortizată se recalculează până la nivelul celei stabilite pe baza valorii de piață a bunului adus ca aport — legea nu permite „coborârea" bazei fiscale sub acest reper prin simple reevaluări descendente.
- Din momentul stabilirii, amortizarea fiscală urmează aceleași reguli generale ca pentru orice alt mijloc fix (metodă, durată normală de funcționare din Catalogul HG 2139/2004, începere de la luna următoare punerii în funcțiune).

## Ce se greșește în practică

- Se amortizează bunul de la valoarea înscrisă în actul constitutiv la o sumă simbolică sau neevaluată corect, în loc de valoarea de piață rezultată dintr-o evaluare efectivă la data aportului.
- Se ignoră cerința evaluării propriu-zise a bunului adus ca aport (de regulă prin evaluator autorizat, potrivit legii), tratând valoarea de aport ca pe o simplă cifră aleasă de asociați.
- Se lasă valoarea fiscală să scadă sub valoarea de piață a aportului prin reevaluări contabile ulterioare, fără recalcularea impusă de Codul fiscal pentru astfel de situații.

## Ce face iConta.eu

Am verificat în `core/repo_mijloace_fixe.py` (funcția `urca_valoarea`) și `core/reevaluare.py`: aplicația reține valoarea de intrare a unui mijloc fix (`valoare`) și permite reevaluări ulterioare, dar **nu diferențiază explicit „valoarea de aport" ca sursă de proveniență** a valorii de intrare, conform art. 7 pct. 44 lit. c) din Codul fiscal — stabilirea corectă a valorii de piață la data aportului (prin evaluare) și introducerea ei ca valoare inițială rămân, la acest moment, în sarcina contabilului.

[iConta.eu](/)
