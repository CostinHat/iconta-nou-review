---
title: "Cumpărarea de bunuri de la o firmă neînregistrată în scopuri de TVA din UE"
description: "Când o achiziție de la un furnizor UE nu e considerată achiziție intracomunitară taxabilă, pentru că vânzătorul e întreprindere mică în statul lui."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cumpărarea de bunuri de la o firmă neînregistrată în scopuri de TVA din UE

Când furnizorul dintr-un alt stat membru nu are cod valabil de TVA pentru că aplică regimul de scutire pentru întreprinderile mici din statul lui, operațiunea nu se mai tratează ca achiziție intracomunitară taxabilă în România — condiția din lege exclude explicit acest caz.

## Temeiul legal

::: ghid-temei
„Sunt, de asemenea, operațiuni impozabile și următoarele operațiuni efectuate cu plată, pentru care locul este considerat a fi în România [...]: a) o achiziție intracomunitară de bunuri, altele decât mijloace de transport noi sau produse accizabile, efectuată de o persoană impozabilă [...], care urmează unei livrări intracomunitare efectuate în afara României de către o persoană impozabilă ce acționează ca atare și care nu este considerată întreprindere mică în statul membru în care are loc livrarea [...]."
— Legea 227/2015 (Codul fiscal), art. 268 alin. (3) lit. a) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.html)
:::

Ce rezultă concret din formulare:

- **Condiția „nu este considerată întreprindere mică"** e parte din definiția legală a operațiunii impozabile — dacă vânzătorul aplică regimul de scutire pentru întreprinderi mici în statul lui de reședință (motiv obișnuit pentru absența unui cod de TVA), livrarea sa nu generează o achiziție intracomunitară taxabilă pentru cumpărătorul din România.
- **Consecința practică**: cumpărătorul român nu aplică taxare inversă și nu raportează operațiunea ca achiziție intracomunitară — vânzarea se tratează, de regulă, ca o vânzare locală în statul furnizorului, sub regimul lui de scutire.
- **Diferit e cazul unui furnizor înregistrat în scopuri de TVA** dar care omite, din eroare, să comunice codul valabil — acolo achiziția intracomunitară taxabilă există, doar identificarea codului trebuie clarificată, nu natura operațiunii.

## Ce se greșește în practică

- Se aplică automat taxare inversă (ca la orice achiziție intracomunitară) pentru orice furnizor din UE fără cod de TVA, fără a verifica dacă absența codului se datorează statutului de întreprindere mică în statul de origine (art. 268 alin. 3 lit. a).
- Se solicită furnizorului un cod de TVA pe care acesta, legal, nu îl are — o întreprindere mică sub plafonul de scutire al propriului stat membru nu e obligată să se înregistreze.
- Se confundă acest caz cu achizițiile de la persoane fizice sau neimpozabile, care au un regim diferit — aici vânzătorul e o persoană impozabilă, doar scutită de înregistrare în TVA în statul ei.

## Ce face iConta.eu

iConta.eu clasifică partenerii de achiziție intracomunitară după codul de TVA comunicat, distingând între „RO_TVA", „NEINREG" și „STRAIN" în motorul de reconciliere D394 (`core/d394_reconciliere.py`). Nu am identificat însă o verificare automată care să determine, pentru un furnizor UE fără cod de TVA, dacă absența codului se datorează statutului de întreprindere mică în statul lui de origine (condiția din art. 268 alin. 3 lit. a) — această distincție, esențială pentru tratamentul corect al operațiunii, rămâne o verificare pe care contabilul o face manual, la nivelul fiecărei tranzacții.

[iConta.eu](/)
