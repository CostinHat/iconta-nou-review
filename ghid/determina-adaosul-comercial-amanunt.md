---
title: "Cum se determină adaosul comercial la amănunt"
description: "Explicație pas cu pas a coeficientului de repartizare a adaosului comercial (K) la comercianții cu amănuntul care țin gestiunea la preț de vânzare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se determină adaosul comercial la amănunt

La metoda global-valorică (preț cu amănuntul), adaosul comercial nu se stabilește produs cu produs, ci printr-un coeficient unic, calculat cumulat pe exercițiul financiar și aplicat la nivelul întregii gestiuni (sau al grupei de stocuri urmărite).

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 286 alin. (4): „Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100."

nota *2) la alin. (4): „La calcularea procentului mediu de adaos comercial, soldul inițial al contului de mărfuri și valoarea intrărilor de mărfuri nu vor include TVA neexigibilă."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Practic, coeficientul se determină din două componente cumulate de la 1 ianuarie:

- **la numărător**: soldul inițial și rulajul de credit al contului 378 „Diferențe de preț la mărfuri" (adaosul comercial existent + adaosul aferent intrărilor din perioadă);
- **la numitor**: soldul inițial și rulajul de debit al contului 371 „Mărfuri" (stocul la preț de înregistrare), din care se scade soldul inițial și rulajul de credit al contului 4428 „TVA neexigibilă" — excludere cerută explicit de nota *2).

Formula folosită de motorul de calcul al iConta.eu (marcată ca interpretare cu temei legal, nu ca citat literal, întrucât OMFP 1802 nu scrie simbolurile 371/378/4428 în text):

```
K = (Si378 + Rc378) / [(Si371 + Rd371) - (Si4428 + Rc4428)]
```

**Exemplu simplu, confirmat prin testare** (`core/test_stocuri.py`, `test_k_simplu`): Si378 = 0, Rc378 = 500, Si371 = 0, Rd371 = 1.785, Si4428 = 0, Rc4428 = 285 → K = 500 / (1.785 − 285) = 500 / 1.500 = 0,3333...

**Exemplu cu solduri inițiale** (`test_descarcare_cu_solduri_initiale`): Si378 = 200, Rc378 = 300, Si371 = 1.000, Rd371 = 1.420, Si4428 = 190, Rc4428 = 230 → numitor = (1.000 + 1.420) − (190 + 230) = 2.000, K = 500 / 2.000 = 0,25.

## Ce se greșește în practică

- Calcularea coeficientului doar din rulajul lunii curente, nu cumulat de la începutul exercițiului financiar, așa cum cere alin. (4).
- Uitarea excluderii TVA neexigibile (4428) din numitor.
- Tratarea unui numitor zero sau negativ ca „adaos 0" sau ca eroare ignorată, în loc de semnal că datele de intrare (solduri, rulaje) sunt greșite sau incomplete.

## Ce face iConta.eu

Funcția `coeficient_k` din `core/stocuri.py` calculează exact raportul de mai sus. Dacă numitorul rezultă mai mic sau egal cu zero, funcția **refuză să calculeze** și aruncă o eroare explicită către contabil — nu întoarce niciodată 0 sau o valoare implicită. Coeficientul astfel obținut este folosit apoi de nota lunară de descărcare de gestiune, generată automat ca ciornă și validată manual de contabil.

[iConta.eu](/)
