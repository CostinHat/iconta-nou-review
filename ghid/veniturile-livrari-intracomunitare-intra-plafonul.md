---
title: Veniturile din livrări intracomunitare intră în plafonul micro?
description: Da — o livrare intracomunitară scutită de TVA (art. 294 alin. 2 lit. a) rămâne un venit din exploatare; scutirea de TVA nu înseamnă excluderea venitului din calculul veniturilor totale pentru încadrarea ca microîntreprindere, care e un impozit distinct.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Veniturile din livrări intracomunitare intră în plafonul micro?

Da. Scutirea de TVA a livrării intracomunitare (art. 294 alin. (2) lit. a) din Codul fiscal) e o regulă de TVA — spune că nu se colectează taxă pe operațiune, cu păstrarea dreptului de deducere. Nu spune nimic despre impozitul pe veniturile microîntreprinderilor, care se calculează pe alt temei, la venitul realizat, nu la taxa colectată.

## Temeiul legal

::: ghid-temei
„Scutire LIC cu drept de deducere — condiții: cod TVA valid al cumpărătorului comunicat furnizorului + dovada transportului în alt SM.” — CF art. 294 alin. (2) lit. a) (sursă: `cod_fiscal_227_2015_consolidat.txt`, L18397+, citat direct și în docstring-ul `core/intracomunitar.py`, verificat în dosarul F050).
:::

Textul de mai sus arată exact ce reglementează art. 294 alin. (2) lit. a): condițiile scutirii de **TVA**. Venitul din vânzare — baza pe care se facturează, cu sau fără TVA — rămâne un venit din activitatea economică a firmei. Faptul că nu poartă TVA colectat nu îl scoate din veniturile din exploatare.

**Notă de onestitate:** ca și la întrebarea echivalentă pentru servicii, acest dosar de cercetare (F050) acoperă latura de TVA a operațiunilor intracomunitare și nu conține un citat verificat din Titlul III al Codului fiscal, care reglementează impozitul pe veniturile microîntreprinderilor și baza lui de calcul. Răspunsul de mai sus e principiul general — venitul din vânzare intră în veniturile totale relevante pentru încadrare, indiferent de regimul de TVA al operațiunii —, nu un citat din acest dosar. Pragul exact și excepțiile limitativ enumerate la calculul veniturilor totale se verifică separat, la data încadrării.

## Ce se greșește în practică

Confuzia tipică e să se echivaleze „scutit de TVA” cu „nu se numără ca venit” — cele două nu au legătură. O altă confuzie, distinctă: pragul de 10.000 euro de la art. 268 din Codul fiscal privește **achizițiile** intracomunitare de bunuri și declanșează obligația de înregistrare specială art. 317 pentru neplătitori; nu are legătură cu plafonul de venituri al regimului micro și nu se aplică livrărilor.

## Ce face iConta.eu

Vectorul fiscal al firmei (`operatiuni_ic`, `inreg_art317`) tratează identic operațiunile intracomunitare indiferent de regimul de impozitare — nu există, în codul citit, o ramură specifică regimului micro care ar trata diferit veniturile din livrări intracomunitare. Calculul veniturilor totale pentru încadrarea sau menținerea ca microîntreprindere e o funcționalitate separată de F050 (operațiuni intracomunitare), pe care acest dosar nu a cercetat-o și nu o descriem aici ca funcție dedicată.

[iConta.eu](/)
