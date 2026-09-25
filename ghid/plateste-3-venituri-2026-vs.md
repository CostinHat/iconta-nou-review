---
title: "Cine plătește 3% pe venituri în 2026 vs micro 1%"
description: "De ce distincția 1%/3% de la impozitul pe veniturile microîntreprinderilor nu se mai aplică în 2026, după unificarea cotei prin OUG 89/2025."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cine plătește 3% pe venituri în 2026 vs micro 1%

Întrebarea „cine plătește 3% și cine 1%" avea sens până la finalul anului 2025: cota standard de impozit pe veniturile microîntreprinderilor era de 1% pentru unele firme și de 3% pentru altele (venituri peste 60.000 euro sau anumite coduri CAEN). În 2026, răspunsul corect e altul — pentru că legea s-a schimbat.

## Temeiul legal

::: ghid-temei
„Articolul 51 Cotele de impozitare
(1) Cota de impozit pe veniturile microîntreprinderilor este de 1%.
(la 01-01-2026, Alineatul (1), Articolul 51, Titlul III a fost modificat de Punctul 4., Articolul I din ORDONANȚA DE URGENȚĂ nr. 89 din 23 decembrie 2025, publicată în MONITORUL OFICIAL nr. 1203 din 24 decembrie 2025)
(1^1) Abrogat.
(la 01-01-2026, [...] a fost abrogat de Punctul 5., Articolul I din ORDONANȚA DE URGENȚĂ nr. 89 din 23 decembrie 2025 [...])"
— Codul fiscal (Legea 227/2015), art. 51 alin. (1), astfel cum a fost modificat de OUG 89/2025 (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Concret, pentru 2026:

- **De la 1 ianuarie 2026, cota unică de impozit pe veniturile microîntreprinderilor este 1%.** OUG 89/2025 a abrogat alineatele care susțineau fosta diferențiere 1%/3% (după plafonul de venituri de 60.000 euro sau după codurile CAEN „sensibile" — IT, HORECA, activități juridice, medicale).
- Nu mai există, în 2026, nicio categorie de microîntreprindere care să plătească legal 3% din venituri. Orice firmă care se încadrează la sistemul de impunere pe veniturile microîntreprinderilor plătește 1%.
- Firmele care ies din micro (ex. prin depășirea plafonului de venituri de 100.000 euro, coborât prin OUG 8/2026) nu trec la „3% micro", ci direct la **impozit pe profit** (16%, sau regimul aplicabil), conform art. 52 din Codul fiscal.

**Notă onestă:** dacă întrebarea are în vedere o cotă de 3% dintr-un alt context fiscal (nu impozitul pe veniturile microîntreprinderilor), acel context nu e acoperit de acest ghid — sursele consultate confirmă unificarea la 1% doar pentru impozitul micro, tema explicită a titlului.

## Ce se greșește în practică

- Se calculează impozitul la cota veche de 3% pentru firme cu venituri peste 60.000 euro sau cu coduri CAEN din fosta listă — regula a fost abrogată de la 1 ianuarie 2026.
- Se caută în declarația D101/formularul de micro o rubrică separată pentru „cota 3%" — nu mai există distincția în formă legală curentă.
- Se confundă ieșirea din micro (trecere la impozit pe profit) cu o simplă schimbare de cotă în interiorul sistemului micro.

## Ce face iConta.eu

La data acestui ghid, iConta.eu **aplică cota unică de 1%** pentru firmele înregistrate în sistemul de impunere pe veniturile microîntreprinderilor, aliniat cu OUG 89/2025. Modulele care ating impozitul pe veniturile microîntreprinderilor (testate în `core/test_a8_micro_baza.py` și `core/test_note_explicative_micro.py`) nu mai calculează varianta 3%, considerată abrogată pentru anul fiscal curent.

[iConta.eu](/)
