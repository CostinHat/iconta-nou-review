---
title: Cum se taxează tichetele de masă în 2026?
description: Tichetele de masă sunt taxate cu CASS 10% reținut din valoarea nominală, apoi impozit 10% pe ce rămâne după CASS, fără CAS și fără CAM — un mecanism de calcul în doi pași, diferit de cel al salariului de bază.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se taxează tichetele de masă în 2026?

Mecanismul de taxare a tichetelor de masă e simplu, dar ordinea contează: CASS se reține primul, din valoarea nominală, iar impozitul se aplică abia pe ce rămâne. Nu se aplică nici CAS, nici CAM.

## Temeiul legal

::: ghid-temei
Codul fiscal (Legea 227/2015, consolidat), Articolul 64:

> „Cota de impozit este de 10% și se aplică asupra venitului impozabil corespunzător fiecărei surse din fiecare categorie pentru determinarea impozitului pe veniturile din:..."

Articolul 142 lit. r (excludere din baza CAS):

> „r) biletele de valoare sub forma tichetelor de masă, voucherelor de vacanță, tichetelor de creșă, tichetelor culturale, acordate potrivit legii;"

Articolul 157 alin. (2) (baza CASS — aici e reintrodusă CASS pe tichete de masă din 2024):

> „(2) Nu se cuprind în baza lunară de calcul al contribuției de asigurări sociale de sănătate sumele prevăzute la art. 76 alin. (4) lit. d), art. 141 lit. d) și art. 142, cu excepția sumelor reprezentând valoarea nominală a biletelor de valoare sub forma tichetelor de masă și a voucherelor de vacanță, acordate potrivit legii."

Legea nr. 201/2025, plafonul valorii nominale:

> „Valoarea nominală a unui tichet de masă nu poate depăși suma de 45 lei."
:::

## Formula de calcul, pas cu pas

1. Se calculează valoarea totală a tichetelor din lună: valoare nominală (până la 45 lei) × număr de zile efectiv lucrate.
2. Se reține CASS 10% din această valoare.
3. Baza de impozit este valoarea tichetelor minus CASS reținut.
4. Se aplică impozitul de 10% pe această bază.
5. Nu se aplică CAS și nici CAM — tichetele de masă sunt excluse explicit din aceste baze.

::: ghid-exemplu
Tichete de masă în valoare de 945 lei într-o lună (45 lei × 21 zile). CASS 10% = 94,5 lei. Bază impozit = 945 − 94,5 = 850,5 lei. Impozit 10% = 85,05 lei. Total reținut = 179,55 lei; suma netă din tichete = 765,45 lei.
:::

## Ce se greșește în practică

- Se calculează impozitul de 10% direct pe valoarea brută a tichetelor, sărind peste scăderea CASS.
- Se aplică CAM pe tichetele de masă, deși nu există bază legală pentru asta — CAM se aplică doar pe venitul salarial obișnuit.
- Se tratează tichetele de masă ca un „avantaj în natură" generic (regimul de la art. 76 alin. 3), deși legea le dă un regim special, separat de enumerarea generică a avantajelor.
- Se omite CASS de 10%, aplicând regimul anterior anului 2024, când tichetele de masă erau excluse și din baza CASS.

## Ce face iConta.eu

Calculul brut→net al aplicației aplică exact acest mecanism pentru tichetele de masă (și pentru voucherele de vacanță, cumulate): CASS 10% pe valoarea nominală, impozit 10% pe baza rămasă după CASS, fără CAS și fără CAM. Regimul e documentat explicit în tabelul intern de tratament al biletelor de valoare din motorul de calcul al salarizării, care distinge tichetele de masă/vacanță (fără CAS, cu CASS 10%, fără CAM) de cadourile peste plafon (tratate ca venit salarial complet, cu CAS, CASS, CAM și impozit).

[iConta.eu](/)
