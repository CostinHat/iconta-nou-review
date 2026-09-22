---
title: Cum completez D212 pentru întreprindere individuală?
description: Întreprinderea individuală (II) se declară exact ca un PFA — venit net în sistem real, CAS peste 12 salarii minime, CASS conform art. 170, impozit 10% — pentru că din punct de vedere fiscal II se încadrează la aceeași categorie de venit, activități independente.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum completez D212 pentru întreprindere individuală?

Din punct de vedere al Codului fiscal, întreprinderea individuală (II) nu are un regim separat de PFA — amândouă intră la aceeași categorie de venit, "activități independente" (art. 155 alin. (1) lit. b)), și se supun acelorași reguli de calcul al venitului net, CAS, CASS și impozit. Diferențele dintre PFA și II țin de dreptul civil/comercial (răspundere, înregistrare), nu de mecanismul de calcul din D212.

## Temeiul legal

::: ghid-temei
**Art. 68 alin.(1):** "Venitul net anual din activități independente se determină în sistem real, pe baza datelor din contabilitate, ca diferență între venitul brut și cheltuielile deductibile efectuate în scopul realizării de venituri, cu excepția situațiilor în care sunt aplicabile prevederile art. 68^1, 68^3 și 69."

**Art. 64 alin.(1):** "Cota de impozit este de 10% și se aplică asupra venitului impozabil corespunzător fiecărei surse din fiecare categorie pentru determinarea impozitului pe veniturile din: a) activități independente; ..."
:::

## Structura declarației

D212 are mai multe capitole, dar pentru o II care lucrează în sistem real contează în principal:

- **Capitolul 11** — sistemul real: venit brut, cheltuieli deductibile, venit net anual, CAS, CASS, impozit. Acesta e capitolul pe care iConta.eu îl completează automat cu cifre calculate.
- **Capitolul 12** — normă de venit (dacă II ar fi optat pentru normă, ceea ce e rar pentru II și nu e cazul tratat aici).
- **Capitolul 14** — venituri din străinătate, dacă e cazul.

Anul de venit contează: structura de plafoane (salariul minim de referință, pragul CASS de 60 sau 72 de salarii minime) diferă între 2025 și 2026.

## Ce se greșește în practică

- Se crede greșit că II are cote sau plafoane diferite de PFA — nu are; regulile din art. 64, 68, 148 și 170 se aplică identic.
- Se completează capitolul de normă de venit din inerție, deși II ține contabilitate în sistem real și trebuie să apară la capitolul 11.
- Se omit cheltuielile validate cu documente justificative din cauza confuziei privind ce categorie de cheltuială e deductibilă integral și ce e limitată (protocol, burse, cheltuieli sociale).
- Se declară un an de venit pentru care plafonul salariului minim de referință nu a fost verificat corect (de exemplu se folosește salariul minim de la 1 iulie în loc de cel valabil, în practică, la 1 ianuarie al anului de venit — reper care nu apare explicit în textul legal citat, deci de tratat cu prudență, nu ca regulă certă).

## Ce face iConta.eu

Motorul de calcul (`core/d212_engine.py`) tratează II identic cu PFA: ia venitul brut din încasările validate legate de activitate și cheltuielile deductibile din plățile validate, calculează venitul net, apoi CAS, CASS și impozitul pe cele 10% cotă. Generatorul XML (`core/d212.py`) populează capitolul 11 (sistem real) cu aceste cifre; capitolul 12 (normă de venit) rămâne cu structura definită în XML, dar fără o funcție de calcul dedicată în motor — nu se completează automat pentru normă de venit. Motorul acceptă doar venituri din 2025 sau 2026; pentru orice alt an, verifică manual sursele oficiale înainte de a declara.

[iConta.eu](/)
