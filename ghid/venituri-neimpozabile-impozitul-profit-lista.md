---
title: "Venituri neimpozabile la impozitul pe profit: lista completă 2026"
description: "Codul fiscal enumeră explicit, la art. 23, categoriile de venituri care nu se impozitează la calculul rezultatului fiscal — de la dividende primite până la venituri din reevaluarea mijloacelor fixe."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Venituri neimpozabile la impozitul pe profit: lista completă 2026

Nu toate veniturile înregistrate contabil intră în calculul impozitului pe profit. Codul fiscal are o listă limitativă de venituri neimpozabile — dacă un venit nu se regăsește pe această listă, regula generală (impozabil) se aplică implicit.

## Temeiul legal

::: ghid-temei
„La calculul rezultatului fiscal, următoarele venituri sunt neimpozabile: a) dividendele primite de la o persoană juridică română; [...] d) veniturile din anularea, recuperarea, inclusiv refacturarea cheltuielilor pentru care nu s-a acordat deducere, veniturile din reducerea sau anularea provizioanelor pentru care nu s-a acordat deducere, veniturile din restituirea ori anularea unor dobânzi și/sau penalități pentru care nu s-a acordat deducere [...]; g) veniturile reprezentând creșteri de valoare rezultate din reevaluarea mijloacelor fixe, terenurilor, imobilizărilor necorporale, după caz, care compensează cheltuielile cu descreșterile anterioare aferente aceleiași imobilizări."
— Legea nr. 227/2015 (Codul fiscal), art. 23 lit. a), d), g) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

- Lista de la art. 23 e **limitativă**: dividendele primite de la persoane juridice române (lit. a), în anumite condiții și cele de la persoane juridice străine dintr-un stat terț cu convenție de evitare a dublei impuneri (lit. b), venituri din majorarea titlurilor de participare prin încorporarea rezervelor (lit. c), venituri din anularea cheltuielilor/provizioanelor pentru care nu s-a acordat deducere (lit. d), venituri din impozitul pe profit amânat pentru contribuabilii la IFRS (lit. e), venituri din modificarea valorii juste a investițiilor imobiliare/activelor biologice la IFRS (lit. f), venituri din reevaluarea mijloacelor fixe care compensează descreșteri anterioare (lit. g), și altele enumerate până la lit. s).
- Regula de bază pentru veniturile din **anularea cheltuielilor nedeductibile** (lit. d) e simetrică: dacă cheltuiala inițială nu a fost dedusă fiscal, venitul din anularea/recuperarea ei nu se impozitează din nou — altfel s-ar impozita de două ori aceeași sumă.
- Veniturile din **reevaluare** (lit. g) sunt neimpozabile doar în măsura în care compensează o descreștere de valoare anterioară a aceleiași imobilizări, înregistrată pe cheltuieli — nu orice creștere din reevaluare e automat neimpozabilă.
- Un venit care nu se regăsește explicit pe lista art. 23 rămâne, implicit, **impozabil**, chiar dacă pare „firesc" să nu fie taxat.

## Ce se greșește în practică

- Se presupune că orice venit „financiar" sau „extraordinar" e automat neimpozabil, fără să se verifice dacă se încadrează efectiv la una din literele art. 23.
- Se tratează ca neimpozabil venitul din anularea unei cheltuieli care, de fapt, fusese dedusă fiscal la momentul înregistrării — condiția simetriei (cheltuiala inițială nedeductibilă) se ignoră.
- Se declară neimpozabilă întreaga creștere din reevaluarea unui mijloc fix, deși legea limitează scutirea la partea care compensează o descreștere anterioară a aceleiași imobilizări.

## Ce face iConta.eu

La data acestui ghid, iConta.eu ține evidența contabilă a veniturilor pe conturile din planul de conturi și calculează impozitul pe profit în modulul D101 (`core/d101.py`) pornind de la rezultatul contabil. Nu am găsit însă o listă de verificare automată care să clasifice fiecare venit înregistrat drept impozabil sau neimpozabil conform art. 23 și să ajusteze automat baza de calcul — încadrarea fiecărui venit pe categoriile din lege rămâne o decizie a contabilului, reflectată apoi manual în calculul rezultatului fiscal.

[iConta.eu](/)
