---
title: "Calculul adaosului comercial la ieșirea din gestiune"
description: "Cum se calculează, la ieșirea mărfii din gestiune, adaosul comercial (378) și TVA neexigibilă (4428) la comercianții care țin evidența la preț de vânzare cu amănuntul."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Calculul adaosului comercial la ieșirea din gestiune

Comercianții care țin evidența mărfurilor la preț de vânzare (metoda global-valorică, „la amănunt") nu cunosc direct costul de achiziție al mărfii vândute — el trebuie extras din prețul de vânzare prin scăderea adaosului comercial și a TVA neexigibile aferente. Iată cum se face corect acest calcul și cum îl automatizează iConta.eu.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 286 alin. (4): „Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100."

pct. 286 alin. (7): „Diferențele de preț se repartizează proporțional atât asupra valorii bunurilor ieșite, cât și asupra bunurilor rămase în stoc."

nota *2) la alin. (4): „La calcularea procentului mediu de adaos comercial, soldul inițial al contului de mărfuri și valoarea intrărilor de mărfuri nu vor include TVA neexigibilă."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Legea cere un coeficient de repartizare cumulat de la începutul exercițiului financiar, calculat ca raport între diferențele de preț (adaosul) acumulate și valoarea stocurilor la preț de înregistrare, din care se exclude TVA neexigibilă (nota *2). Acest coeficient se aplică apoi proporțional, atât asupra mărfii ieșite (vândute), cât și asupra celei rămase în stoc (alin. 7).

Codul iConta.eu transpune această regulă astfel (marcată explicit ca interpretare cu temei, nu ca citat literal din lege, deoarece OMFP 1802 nu scrie formula cu simbolurile conturilor 371/378/4428):

```
K = (Si378 + Rc378) / [(Si371 + Rd371) - (Si4428 + Rc4428)]
Adaos descărcat (378) = K × Rc707
4428 descărcat = TVA aferentă vânzărilor
607 = Rc707 - 378 descărcat
```

unde `Si` = sold inițial, `Rc`/`Rd` = rulaj credit/debit, calculate cumulat de la 1 ianuarie. Scăderea 4428 din numitor corespunde matematic excluderii TVA neexigibile cerute de nota *2).

**Exemplu confirmat prin testare** (`core/test_stocuri.py`): stoc 371 = 1.785 lei (cost 1.000 + adaos 500 + TVA neexigibilă 285), se vinde toată marfa (Rc707 = 1.500, TVA colectată = 285). Coeficientul K = 500/1.500 = 0,3333, adaosul descărcat = 500,00 lei, costul mărfii vândute (607) = 1.000,00 lei, TVA descărcată (4428) = 285,00 lei — contul 371 se golește complet (1.785,00).

## Ce se greșește în practică

- Calcularea adaosului „pe fiecare produs vândut", în loc de coeficient cumulat pe exercițiu financiar aplicat la nivelul rulajelor lunii.
- Includerea TVA neexigibile (4428) în baza de calcul a coeficientului, contrar notei *2) de la alin. (4).
- Ignorarea faptului că un numitor zero sau negativ (stoc epuizat sau date greșite) nu are o soluție „implicită" — calculul trebuie oprit și verificat, nu forțat cu o valoare aproximativă.

## Ce face iConta.eu

Motorul de calcul (`core/stocuri.py`) implementează exact formula de mai sus prin funcția `descarcare_gv`, care se bazează la rândul ei pe `coeficient_k`. Dacă numitorul `(Si371 + Rd371) - (Si4428 + Rc4428)` este mai mic sau egal cu zero, aplicația **refuză să calculeze** și afișează o eroare explicită către contabil, în loc să întoarcă 0 sau o valoare implicită. Dacă rezultă un cost al mărfii vândute negativ (adaos peste 100%), aplicația generează de asemenea o eroare explicită.

Nota de descărcare (607 = 371, 378 = 371, 4428 = 371) este propusă automat de aplicație ca **ciornă**; ea trebuie validată manual de contabil în jurnal — aplicația nu validează singură notele contabile.

[iConta.eu](/)
