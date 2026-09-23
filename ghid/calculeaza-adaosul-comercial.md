---
title: Cum se calculează adaosul comercial?
description: Adaosul comercial descărcat lunar se calculează prin coeficientul de repartizare K = diferențe de preț (sold inițial + intrări) / (stoc la preț de înregistrare − TVA neexigibilă), cumulat de la 1 ianuarie, înmulțit apoi cu vânzările lunii.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează adaosul comercial?

Adaosul comercial (marja comerciantului) se stabilește, la fiecare recepție, ca diferență decisă de firmă între prețul de vânzare și costul de achiziție. Dar întrebarea reală, în gestiunea la preț cu amănuntul, e alta: **cât din adaosul total acumulat în stoc trebuie „descărcat” lunar**, proporțional cu ce s-a vândut efectiv — iar aici intervine coeficientul de repartizare.

## Temeiul legal

::: ghid-temei
„Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100.”

„nota *2): La calcularea procentului mediu de adaos comercial, soldul inițial al contului de mărfuri și valoarea intrărilor de mărfuri nu vor include TVA neexigibilă.”

„(7) Diferențele de preț se repartizează proporțional atât asupra valorii bunurilor ieșite, cât și asupra bunurilor rămase în stoc.”

— *OMFP 1802/2014, pct. 286 alin. (4) și (7).*
:::

## Formula, pas cu pas

1. **Calculați coeficientul K**, cumulat de la 1 ianuarie până la finalul lunii de referință:
   `K = (Sold inițial 378 + Rulaj credit 378) / [(Sold inițial 371 + Rulaj debit 371) − (Sold inițial 4428 + Rulaj credit 4428)]`
   — numărătorul e adaosul acumulat (378); numitorul e stocul la preț de înregistrare, din care se scade explicit TVA neexigibilă (4428), conform notei 2) de la alin. (4).
2. **Aplicați K la vânzările lunii** (rulajul creditor al contului 707, doar pe luna curentă, nu cumulat): `Adaos descărcat = K × Vânzări lunare (707)`.
3. **Costul mărfii vândute** rezultă prin diferență: `CMV = Vânzări (707) − Adaos descărcat`.

::: ghid-exemplu
Sold inițial 378 = 200 lei, rulaj credit 378 (intrări cu adaos) = 300 lei. Sold inițial 371 = 1.000 lei, rulaj debit 371 = 1.420 lei. Sold inițial 4428 = 190 lei, rulaj credit 4428 = 230 lei.
Numărător = 200 + 300 = 500 lei. Numitor = (1.000 + 1.420) − (190 + 230) = 2.420 − 420 = 2.000 lei.
K = 500 / 2.000 = 0,25 (25%).
Dacă vânzările lunii (707) sunt 400 lei: adaos descărcat = 400 × 0,25 = 100 lei; CMV = 400 − 100 = 300 lei.
:::

## Ce se greșește în practică

- Se calculează coeficientul K doar din datele lunii curente, nu cumulat de la 1 ianuarie — legea cere explicit calcul cumulat pe exercițiul financiar, nu lunar izolat.
- Se include TVA neexigibilă (4428) în numitor — nota 2) de la alin. (4) cere explicit excluderea ei din baza de calcul.
- Se aplică K la vânzările cumulate ale întregului an, nu doar la vânzările lunii curente — dublând, efectiv, adaosul descărcat.
- Se presupune, greșit, că formula exactă cu simbolurile 371/378/4428 e un citat literal din lege — e o transpunere coerentă cu textul (formula generică de la alin. 4, combinată cu nota 2), dar nu o formulă scrisă verbatim în text sub această formă.

## Ce face iConta.eu

Funcția `coeficient_k(si_378, rc_378, si_371, rd_371, si_4428, rc_4428)` din `core/stocuri.py` implementează exact formula de mai sus, cu excluderea explicită a soldului/rulajului 4428 din numitor. Dacă numitorul ajunge la zero sau negativ, funcția **refuză să calculeze** și aruncă o eroare explicită, în loc să întoarcă 0 sau o valoare implicită.

Funcția `descarcare_gv(rc_707, tva_vanzari, ...)` aplică apoi K la vânzările lunii (`adaos = rc_707 × K`, `cmv = rc_707 − adaos`) și generează nota de descărcare (`607=371` pentru CMV, `378=371` pentru adaos, `4428=371` pentru TVA). Dacă nu au fost vânzări în lună (`rc_707 == 0`), nu se generează nicio notă „pe zero”. Calculul din `descarca_luna` (`core/stocuri_api.py`) ia soldurile inițiale din tabela `solduri_initiale` și rulajele din notele **validate**, cumulat de la 1 ianuarie — confirmând textual regula „cumulat pe exercițiu” din lege.

[iConta.eu](/)
