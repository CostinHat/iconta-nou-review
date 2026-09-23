---
title: Cum se calculează coeficientul K la mărfuri?
description: Formula coeficientului de repartizare (K) folosit la descărcarea de gestiune global-valorică, cu temeiul legal și un exemplu numeric verificat.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se calculează coeficientul K la mărfuri?

Coeficientul K (numit și coeficient de repartizare a diferențelor de preț) este mecanismul prin care se determină ce parte din valoarea vânzărilor lunii reprezintă adaos comercial și ce parte reprezintă costul de achiziție al mărfii vândute, la metoda prețului cu amănuntul.

## Temeiul legal

::: ghid-temei
„Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (4)
:::

::: ghid-temei
„La calcularea procentului mediu de adaos comercial, soldul inițial al contului de mărfuri și valoarea intrărilor de mărfuri nu vor include TVA neexigibilă."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (4), nota *2)
:::

Textul de lege dă formula generică: sold inițial al diferențelor de preț (adaos) plus adaosul aferent intrărilor, raportat la soldul inițial al stocurilor la preț de înregistrare plus intrările la preț de înregistrare, ambele cumulate de la începutul exercițiului. Nota *2) adaugă o precizare importantă: baza de calcul a stocurilor (numitorul) **nu trebuie să includă TVA neexigibilă**.

În aplicație, această regulă se aplică folosind conturile din planul de conturi: adaosul este evidențiat prin contul 378, stocul de mărfuri la preț de înregistrare prin contul 371, iar TVA neexigibilă prin contul 4428. Formula de calcul folosită de motorul de calcul al iConta.eu este:

```
K = (Si378 + Rc378) / [(Si371 + Rd371) - (Si4428 + Rc4428)]
```

unde Si = sold inițial, Rc = rulaj creditor, Rd = rulaj debitor, toate cumulate de la 1 ianuarie. Scăderea soldului și rulajului contului 4428 din numitor este transpunerea, în termeni de conturi, a cerinței din nota *2) ca baza de calcul să nu includă TVA neexigibilă — este o aplicare a regulii legale, nu un citat literal al formulei din text (legea nu scrie formula cu simbolurile 371/378/4428).

## Exemplu numeric

Pentru un stoc fără solduri inițiale (Si378 = 0, Si371 = 0, Si4428 = 0) și rulaje de intrări Rc378 = 500, Rd371 = 1785, Rc4428 = 285:

```
K = 500 / (1785 - 285) = 500 / 1500 = 0,3333...
```

## Ce se greșește în practică

- Se calculează K raportând adaosul direct la soldul contului 371, fără a scădea TVA neexigibilă din numitor — rezultatul iese subevaluat față de cerința legală a notei *2).
- Se calculează K pe o singură lună, izolat, în loc de cumulat de la începutul exercițiului financiar, așa cum cere explicit textul legal.

## Ce face iConta.eu

Coeficientul se calculează automat, cumulat de la 1 ianuarie, din soldurile inițiale și rulajele reale, validate, ale conturilor 371, 378 și 4428. Dacă numitorul rezultă zero sau negativ, aplicația refuză explicit calculul și afișează o eroare către contabil, în loc să întoarcă o valoare implicită sau zero.

[iConta.eu](/)
