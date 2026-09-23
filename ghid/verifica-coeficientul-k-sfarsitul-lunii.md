---
title: Cum se verifică coeficientul K la sfârșitul lunii?
description: Ce verifică motorul de calcul înainte de a propune coeficientul K, și cum poate contabilul controla rezultatul înainte de validarea notei de descărcare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se verifică coeficientul K la sfârșitul lunii?

Coeficientul K este calculat automat de aplicație, dar rămâne ultima ocazie de verificare contabilă înainte ca nota de descărcare de gestiune să devină nemodificabilă (odată validată, nota nu mai poate fi editată sau ștearsă din aplicație).

## Temeiul legal

::: ghid-temei
„Diferențele de preț se repartizează proporțional atât asupra valorii bunurilor ieșite, cât și asupra bunurilor rămase în stoc."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (7)
:::

Coeficientul K aplicat vânzărilor lunii trebuie să reflecte aceeași proporție de adaos care rămâne, în același timp, în stocul nevândut — de aceea el se calculează din soldurile și rulajele cumulate ale conturilor, nu dintr-o valoare stabilită separat pentru fiecare vânzare.

## Ce verifică motorul de calcul înainte de a propune un rezultat

- **Numitorul formulei** — soldul stocurilor la preț de înregistrare, din care s-a scăzut TVA neexigibilă — trebuie să fie pozitiv. Dacă e zero sau negativ, aplicația **refuză să calculeze** și aruncă o eroare explicită către contabil, în loc să întoarcă 0 sau o valoare implicită.
- **Rezultatul descărcării** — dacă un coeficient K mai mare decât 1 ar duce la un cost al mărfii vândute negativ, aplicația refuză explicit și acest calcul.
- **Absența vânzărilor** — dacă nu au existat vânzări în luna respectivă, nu se generează nicio notă „pe zero", ceea ce înseamnă că lipsa unei note de descărcare pentru o lună poate avea și o explicație validă: pur și simplu nu au fost vânzări.

## Cum verifică manual contabilul

Cea mai directă verificare e recalcularea manuală a formulei, pornind de la soldurile și rulajele cumulate afișate de aplicație pentru conturile 371, 378 și 4428, de la 1 ianuarie până la finalul lunii verificate. De exemplu, pentru solduri inițiale Si378 = 200, Rc378 = 300, Si371 = 1000, Rd371 = 1420, Si4428 = 190, Rc4428 = 230:

```
numitor = (1000 + 1420) - (190 + 230) = 2000
K = (200 + 300) / 2000 = 500 / 2000 = 0,25
```

Cu acest K, pentru vânzări ale lunii de 400, rezultă adaos descărcat de 100 și cost al mărfii vândute de 300 — valori pe care contabilul le poate compara direct cu nota propusă de aplicație, înainte de validare.

## Ce se greșește în practică

- Se validează nota fără a recalcula măcar o dată coeficientul K din soldurile afișate, ceea ce elimină ultima ocazie de a prinde o eroare înainte ca nota să devină nemodificabilă.
- Se ignoră posibilitatea ca rulajul contului 4428 să conțină și mișcări nelegate de gestiunea de mărfuri (de exemplu, note manuale de TVA la încasare), ceea ce ar denatura numitorul fără ca aplicația să semnaleze automat acest amestec.

## Ce face iConta.eu

Coeficientul K, adaosul descărcat, costul mărfii vândute și TVA neexigibilă aferentă sunt afișate în nota propusă (ciornă) înainte de validare, pornind mereu de la soldurile și rulajele cumulate reale, validate deja în jurnal. Contabilul are la dispoziție acest interval — de la propunerea notei până la validarea ei — ca fereastră de verificare.

[iConta.eu](/)
