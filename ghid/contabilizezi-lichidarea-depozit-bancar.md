---
title: Cum contabilizezi lichidarea unui depozit bancar
description: Depozitul bancar în valută se constituie și se lichidează la cursul BNR din ziua fiecărei operațiuni; diferența dintre cursul de constituire și cel de lichidare se recunoaște la venituri sau cheltuieli financiare din diferențe de curs valutar.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum contabilizezi lichidarea unui depozit bancar

Pentru depozitele în lei, lichidarea e simplă — se transferă suma și dobânda din contul de depozit în contul curent, fără complicații de evaluare. Pentru depozitele în valută, intervine întotdeauna un calcul de diferență de curs.

### Constituirea depozitului

Conform Reglementărilor contabile aprobate prin OMFP 1802/2014, pct. 295 alin. (2):

> „Depozitele bancare pe termen scurt în valută se înregistrează la constituire **la cursul de schimb valutar comunicat de Banca Națională a României, de la data operațiunii de constituire**."

Articolul contabil, la constituire: debit 508 „Alte investiții pe termen scurt și creanțe asimilate" (analitic depozit), credit 512 „Conturi curente la bănci" — la valoarea în lei, calculată la cursul BNR din ziua constituirii.

### Lichidarea depozitului

Pct. 296 din aceleași reglementări tratează explicit lichidarea:

> alin. (1): „**Lichidarea depozitelor constituite în valută se efectuează la cursul de schimb valutar comunicat de Banca Națională a României, de la data operațiunii de lichidare**."
>
> alin. (2): „Diferențele de curs valutar între cursul de la data constituirii sau cursul la care sunt înregistrate în contabilitate și cursul Băncii Naționale a României de la data lichidării depozitelor bancare se înregistrează la **venituri sau cheltuieli din diferențe de curs valutar**, după caz."

Practic, la lichidare:
1. Se calculează valoarea în lei a depozitului la cursul BNR din ziua lichidării.
2. Se compară cu valoarea în lei la care depozitul figurează în contabilitate (cursul de la constituire, sau cursul de la ultima evaluare de închidere de exercițiu, dacă depozitul a rămas deschis peste finalul unui an fiscal).
3. Diferența favorabilă (cursul a crescut) se înregistrează în contul **765/7651** „Diferențe favorabile de curs valutar"; diferența nefavorabilă (cursul a scăzut) în contul **665/6651** „Diferențe nefavorabile de curs valutar", legate de elementele monetare exprimate în valută.

### Monografie simplificată — exemplu

Depozit de 10.000 EUR constituit la curs 4,97 lei/EUR (valoare 49.700 lei):

- **Constituire**: 508 = 512, 49.700 lei.
- **Lichidare**, dacă la data respectivă cursul BNR e 5,02 lei/EUR (valoare 50.200 lei):
  - 512 = 508, 49.700 lei (ieșirea depozitului la valoarea contabilă);
  - 512 = 7651, 500 lei (diferența favorabilă de curs, cursul lichidării fiind mai mare decât cel de constituire).
- Dacă în schimb cursul de lichidare ar fi fost 4,90 lei/EUR (valoare 49.000 lei), diferența de 700 lei ar fi fost nefavorabilă: 6651 = 508, 700 lei.

### Dobânda aferentă

Dobânda încasată la lichidare (dacă nu a fost deja recunoscută pe parcurs, la închideri de lună/exercițiu) se înregistrează separat, la venituri financiare (766 „Venituri din dobânzi"), evaluată la cursul BNR din ziua încasării ei — nu se amestecă în calculul diferenței de curs a capitalului depus.

### Depozitele care rămân deschise la închiderea exercițiului

Pentru depozitele care nu se lichidează în același an în care au fost constituite, ele se reevaluează la închiderea exercițiului financiar la cursul BNR de la acea dată (aceeași regulă de evaluare a elementelor monetare în valută), iar diferența rezultată se înregistrează tot la 665/765 — lichidarea ulterioară va compara valoarea de la ultima evaluare de închidere, nu cea de la constituirea inițială.
