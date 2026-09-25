---
title: "Amenajările de teren se amortizează?"
description: "Diferența fiscală dintre terenuri (neamortizabile) și amenajările de terenuri (amortizabile pe 10 ani), conform Codului fiscal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Amenajările de teren se amortizează?

Terenurile, ca regulă, nu se amortizează fiscal — dar investițiile făcute pentru amenajarea lor (drenaje, împrejmuiri, sisteme de irigații, alei etc.) sunt tratate complet diferit.

## Temeiul legal

::: ghid-temei
„(3) Sunt, de asemenea, considerate mijloace fixe amortizabile: [...] f) amenajările de terenuri; [...]
(4) Nu reprezintă active amortizabile: a) terenurile, inclusiv cele împădurite; [...]
(12) Amortizarea fiscală se calculează după cum urmează: [...] e) pentru cheltuielile cu investițiile efectuate pentru amenajarea terenurilor, liniar, pe o perioadă de 10 ani."
— Legea 227/2015 (Codul fiscal), art. 28 alin. (3) lit. f), alin. (4) lit. a) și alin. (12) lit. e) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă o distincție clară pe care contabilitatea trebuie să o respecte:

- **Terenul propriu-zis** (inclusiv cel împădurit) este exclus expres de la amortizare — valoarea lui rămâne în bilanț neschimbată prin amortizare, indiferent de durata de deținere.
- **Amenajările de terenuri** — investițiile suplimentare făcute pentru a face terenul utilizabil (nivelări, drenaje, sisteme de irigație, împrejmuiri, alei, spații verzi amenajate) — sunt, prin lege, **mijloace fixe amortizabile distincte**.
- Metoda de amortizare pentru amenajările de terenuri este **fixă**: liniară, pe o perioadă de **10 ani** — spre deosebire de alte categorii de mijloace fixe, unde contribuabilul poate opta între metoda liniară, degresivă sau accelerată.
- Contabil, terenurile și amenajările de terenuri se țin pe categorii separate, exact pentru a permite acest tratament diferit (OMFP 1802/2014, pct. 193 alin. (1): „Contabilitatea terenurilor se ține pe două categorii: terenuri și amenajări de terenuri").

## Ce se greșește în practică

- Se include valoarea amenajărilor de teren în valoarea terenului și se tratează tot ansamblul ca neamortizabil, pierzând astfel o deducere legitimă.
- Se amortizează amenajările de teren după o altă metodă (degresivă sau accelerată) sau pe o altă durată decât cei 10 ani impuși explicit de lege pentru această categorie.
- Se înregistrează investiția în amenajări direct pe cheltuieli, fără capitalizare ca mijloc fix distinct.

## Ce face iConta.eu

Am verificat în `core/repo_mijloace_fixe.py` și `core/mijloace_fixe_import_api.py`: aplicația reține durata normală de funcționare (`dnf_luni`) introdusă de contabil pentru fiecare mijloc fix și calculează amortizarea pe baza ei, dar **nu are o categorie predefinită „amenajări de terenuri" cu durata fixă de 10 ani și metoda liniară impuse de art. 28 alin. (12) lit. e)** — încadrarea corectă a unei investiții ca amenajare de teren, separat de valoarea terenului, și aplicarea duratei legale de 10 ani rămân responsabilitatea contabilului la introducerea datelor.

[iConta.eu](/)
