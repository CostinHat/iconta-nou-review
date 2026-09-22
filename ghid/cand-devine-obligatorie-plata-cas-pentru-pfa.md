---
title: Când devine obligatorie plata CAS pentru PFA?
description: CAS (contribuția de asigurări sociale, pensii) devine obligatorie pentru un PFA în sistem real doar dacă venitul net anual atinge cel puțin 12 salarii minime brute pe țară; sub acest prag, plata rămâne opțională.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Când devine obligatorie plata CAS pentru PFA?

CAS (contribuția de asigurări sociale, care alimentează pensia) nu se datorează automat de la primul leu de venit. Legea stabilește un prag anual: doar peste 12 salarii minime brute pe țară CAS devine obligatorie. Această regulă e diferită de cea pentru CASS (sănătate), care are alt prag și alte condiții de obligativitate — nu le confunda.

## Temeiul legal

::: ghid-temei
**Art. 148 alin.(1):** "Persoanele fizice care în anul fiscal ... au realizat venituri din activitățile prevăzute la art. 137 alin. (1) lit. b) și b^1) ... a căror valoare anuală cumulată este cel puțin egală cu 12 salarii minime brute pe țară, datorează contribuția de asigurări sociale la o bază de calcul stabilită potrivit alin. (2)."

**Art. 148 alin.(4):** "Persoanele fizice ... care nu se încadrează în plafonul de cel puțin 12 salarii prevăzut la alin. (3) pot opta pentru plata contribuției de asigurări sociale...".

**Art. 138 lit.a):** "25% datorată de către persoanele fizice care au calitatea de angajați sau pentru care există obligația plății contribuției de asigurări sociale".
:::

## Regula, pe scurt

- **Venit net sub 12 salarii minime** → CAS neobligatorie. Poate fi plătită opțional (util pentru vechime în pensie), caz în care baza de calcul devine automat 12 salarii minime, nu venitul real, mai mic.
- **Venit net de la 12 salarii minime în sus** → CAS obligatorie, la o bază de calcul care urcă în trepte (12 sau 24 de salarii minime, vezi ghidul despre plafon).

Cu salariul minim de referință 4.050 lei (2025/2026), pragul de obligativitate e 48.600 lei venit net anual. În practică se raportează la salariul minim valabil la 1 ianuarie al anului de venit, dar acest reper nu apare explicit ca literă de lege în textul art. 148 — verifică-l cu prudență, nu ca regulă legală certă.

## Ce se greșește în practică

- Se confundă pragul de obligativitate CAS (12 salarii minime) cu cel de la CASS, care are altă structură — CASS e obligatorie practic la orice venit net pozitiv pentru PFA, nu doar peste 6 salarii minime.
- Se crede că sub pragul de 12 salarii minime nu se poate plăti deloc CAS — de fapt se poate opta, doar că nu e obligatoriu.
- Se compară venitul brut cu pragul de 12 salarii minime, în loc de venitul net (după scăderea cheltuielilor deductibile).
- Se ignoră cumulul cu alte venituri din activități independente (alte PFA-uri, contracte sportive) la același plafon, când legea cere verificarea sumei cumulate.

## Ce face iConta.eu

`core/d212_engine.py`, funcția `calculeaza_cas`, aplică exact acest prag: sub 12 salarii minime, întoarce "neobligatoriu" (cu posibilitatea de a opta manual pentru plată, caz în care baza sare la 12 salarii minime); de la 12 salarii minime în sus, CAS devine obligatorie, cu bază plafonată în trepte. Acest comportament e confirmat ca fiind conform art. 148 — spre deosebire de tratamentul CASS din motor, aici nu există nicio discrepanță semnalată față de lege. Ce nu verifică automat motorul: cumulul cu alte surse de venit independent ale aceleiași persoane, care ar trebui adunate la același plafon conform art. 148 alin. (3).

[iConta.eu](/)
