---
title: "Cum se separă TVA pe țări pentru vânzările declarate prin OSS"
description: "Ce cere legea privind defalcarea pe stat membru de consum și pe cotă de TVA a vânzărilor raportate prin regimul special OSS."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se separă TVA pe țări pentru vânzările declarate prin OSS

Regimul special OSS (One Stop Shop) permite unei firme din România să declare, printr-o singură declarație, TVA-ul datorat în mai multe state membre de consum — dar declarația nu e un total agregat. Structura ei impune defalcare pe fiecare stat și pe fiecare cotă de taxă aplicabilă.

## Temeiul legal

::: ghid-temei
„(7) Declarația specială de TVA trebuie să conțină următoarele informații: [...] b) valoarea totală, exclusiv taxa, cotele taxei aplicabile și valoarea totală a taxei corespunzătoare subdivizată pe cote, datorate fiecărui stat membru de consum în care taxa este exigibilă, în ceea ce privește următoarele livrări de bunuri sau prestări de servicii reglementate de prezentul articol, efectuate în cursul perioadei fiscale: 1. vânzările intracomunitare de bunuri la distanță; [...] 3. prestările de servicii; [...] c) valoarea totală a taxei datorate în statele membre de consum."
— Legea nr. 227/2015 (Codul fiscal), art. 315 alin. (7) lit. b)-c) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Practic, „separarea pe țări" nu e o opțiune de raportare, ci structura obligatorie a declarației:

- Pentru **fiecare stat membru de consum** în care taxa devine exigibilă, se raportează separat valoarea vânzărilor (exclusiv taxa) și taxa aferentă.
- În interiorul fiecărui stat, valorile se **subdivizează pe cote** — pentru că multe state UE au mai multe cote de TVA (standard, redusă, super-redusă), iar fiecare cotă aplicabilă apare cu propria bază și propria taxă.
- Declarația se întocmește trimestrial, în euro, folosind cursul de schimb BCE din ultima zi a perioadei de raportare, dacă operațiunile s-au plătit în altă monedă.

## Ce se greșește în practică

- Se raportează un total unic de TVA colectat prin vânzările OSS, fără defalcare pe stat membru — declarația e respinsă sau incompletă, pentru că structura cere granularitate pe fiecare stat și cotă.
- Se confundă cota de TVA românească aplicată intern cu cota din statul membru de consum — fiecare vânzare la distanță se taxează cu cota țării de destinație, nu cu cota din România.
- Se omite subdivizarea pe cote în interiorul aceluiași stat, când firma vinde atât bunuri cu cotă standard, cât și bunuri cu cotă redusă în același stat membru de consum.

## Ce face iConta.eu

Verificat în cod: iConta.eu generează declarația D398 (declarația specială de TVA pentru regimurile speciale UE/non-UE/import — OSS), cu structura citită și probată direct pe validatorul oficial ANAF (modulul `core/d398.py`). Declarația respectă structura pe stat membru de consum (element `MS`) și pe operațiune/cotă (element `SUPPLY`, cu câmpuri `vat_rate`, `taxable_amount`, `vat_amount` pentru fiecare cotă aplicabilă). Important: **aplicația nu ține evidența automată a operațiunilor OSS pe stat de consum și cotă străină** — nu există, la acest moment, o legătură între vânzările înregistrate în facturare și defalcarea lor pe țară/cotă; toate valorile din D398 se introduc manual de către contabil, pe baza propriei evidențe a vânzărilor la distanță.

[iConta.eu](/)
