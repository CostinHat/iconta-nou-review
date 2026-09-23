---
title: Cum se organizează gestiunea la un magazin alimentar?
description: Un magazin alimentar, cu articole numeroase și marje similare, e cazul tipic pentru metoda global-valorică (preț cu amănuntul) — recepție cu cost+adaos+TVA neexigibilă separate, descărcare lunară prin coeficient de adaos; legea nu prevede reguli speciale pentru sectorul alimentar.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se organizează gestiunea la un magazin alimentar?

Un magazin alimentar e exact tipul de activitate pentru care legea a gândit metoda prețului cu amănuntul (global-valorică): sute sau mii de articole diferite, cu mișcare rapidă, unde urmărirea individuală a costului fiecărui produs ar fi nepractică. Nu există, în legislația contabilă verificată, reguli speciale dedicate sectorului alimentar — se aplică mecanismul general de gestiune la preț cu amănuntul.

## Temeiul legal

::: ghid-temei
„(8) În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă. În această situație, costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor.”

— *OMFP 1802/2014, pct. 286 alin. (8).*
:::

## Organizarea gestiunii, pas cu pas

1. **La fiecare recepție de marfă** (NIR), se înregistrează separat costul de achiziție (371=401), TVA deductibilă (4426=401), costurile accesorii precum transportul, dacă există (371=cont accesoriu), adaosul comercial stabilit de magazin (371=378) și TVA aferentă prețului de vânzare (371=4428).
2. **Vânzarea zilnică** se înregistrează, de regulă, global, pe bază de raport de casă/Z, în contul 707 (venituri din vânzarea mărfurilor), fără să fie nevoie de scădere articol cu articol din gestiune la fiecare bon fiscal.
3. **Lunar**, se calculează coeficientul de adaos (K), cumulat de la 1 ianuarie, și se aplică la vânzările lunii pentru a determina cât din încasări reprezintă cost de achiziție și cât reprezintă adaos — nota de descărcare de gestiune se generează la sfârșitul lunii.
4. **Inventarul fizic periodic** rămâne obligatoriu, ca la orice gestiune de mărfuri — coeficientul de adaos calculat teoretic nu înlocuiește verificarea faptică a stocului.

## Ce se greșește în practică

- Se caută o regulă fiscală specifică „pentru alimentare” (TVA redusă, regim special de evidență) care nu există în sursele legale de contabilitate a stocurilor — cotele reduse de TVA la alimente sunt o chestiune separată, de TVA colectată la vânzare, nu de metoda de evidență a gestiunii.
- Se ține evidență cantitativ-valorică, articol cu articol, pentru un magazin cu mii de referințe — posibil, dar ineficient; exact acest caz e cel pentru care legea recomandă metoda global-valorică.
- Se omite separarea adaosului (378) și a TVA-ului neexigibil (4428) la recepție, tratând marfa doar la cost de achiziție — fără această separare, calculul lunar al coeficientului de adaos nu are date corecte.

## Ce face iConta.eu

Pentru un magazin alimentar, motorul relevant e cel de gestiune global-valorică (`core/stocuri.py` + `core/stocuri_api.py`): `nir_gv` pentru recepții (cu cost, adaos, TVA neexigibilă separate pe fiecare linie), `descarcare_gv`/`descarca_luna` pentru descărcarea lunară automată, propusă ca ciornă pentru validare.

Nu am găsit, în `FUNCTIONALITATI.csv` sau în codul verificat, nicio funcționalitate sau particularizare de cod specifică sectorului alimentar (cote speciale, regim distinct de gestiune) — orice specificitate fiscală a comerțului alimentar (dincolo de cota de TVA aplicată la vânzare, calculată separat) nu e implementată ca atare în motorul de stocuri; gestiunea unui magazin alimentar folosește mecanismul general F088, la fel ca orice alt comerț cu amănuntul cu articole numeroase.

[iConta.eu](/)
