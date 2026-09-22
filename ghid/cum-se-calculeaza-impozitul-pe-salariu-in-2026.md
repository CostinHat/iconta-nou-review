---
title: Cum se calculează impozitul pe salariu în 2026?
description: Impozitul pe venit din salarii este 10%, aplicat pe baza impozabilă rămasă după scăderea CAS, CASS și a deducerii personale din brutul impozabil - baza legală directă este art.78 din Codul fiscal, specific veniturilor din salarii.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează impozitul pe salariu în 2026?

Impozitul pe venit din salarii este 10%, dar nu se aplică direct pe salariul brut, ci pe o bază impozabilă mai mică, rămasă după scăderea contribuțiilor obligatorii și a deducerii personale.

## Temeiul legal

::: ghid-temei
**Codul fiscal, Articolul 78, alin.(2) lit.a):** *"la locul unde se află funcția de bază, prin aplicarea cotei de 10% asupra bazei de calcul..."*
:::

## Cum se ajunge la baza impozabilă

Impozitul de 10% nu se aplică pe salariul brut, ci pe o bază de calcul obținută astfel:

1. Din venitul brut impozabil se scade, dacă e cazul, facilitatea pentru salariul minim (200 sau 300 lei, în condițiile legale specifice) → rezultă baza de contribuție.
2. Din baza de contribuție se scad CAS (25%) și CASS (10%).
3. Din rezultat se scade deducerea personală (dacă salariatul are dreptul la ea, în funcție de nivelul brutului și de persoanele în întreținere).
4. Dacă rezultatul e negativ, baza impozabilă devine 0.
5. Impozitul = baza impozabilă × 10%.

Baza legală directă pentru cota de 10% aplicată veniturilor din salarii este art.78 din Codul fiscal, care conține propria formulare, specifică veniturilor salariale ("la locul unde se află funcția de bază, prin aplicarea cotei de 10% asupra bazei de calcul"). Cota de 10% mai apare menționată și ca regulă generală pentru mai multe categorii de venit în alt articol al Codului fiscal, dar pentru salarii, articolul cu formularea cea mai directă și mai ușor de verificat este art.78 alin.(2) lit.a).

::: ghid-exemplu
Un salariat cu brut 5.000 lei, fără persoane în întreținere: acest brut este SUB plafonul de deducere (salariul minim + 2.000 lei = 4.325 + 2.000 = 6.325 lei, H2 2026), deci salariatul beneficiază totuși de o deducere personală, redusă degresiv, nu de deducere zero. CAS = 5.000 × 25% = 1.250 lei, CASS = 5.000 × 10% = 500 lei. Deducerea personală (0 persoane în întreținere: 20% din salariul minim la nivelul salariului minim, redusă cu 0,5 puncte procentuale pentru fiecare tranșă de 50 lei sau fracție peste salariul minim) este, pentru o diferență brut − salariul minim de 675 lei (14 tranșe a 50 lei, rotunjite în sus), de 20% − 14×0,5% = 13%, adică 13% × 4.325 = 562,25 lei. Baza impozabilă = 5.000 − 1.250 − 500 − 562,25 = 2.687,75 lei, iar impozitul = 2.687,75 × 10% = 268,78 lei.
:::

## Ce se greșește în practică

- Se aplică 10% direct pe salariul brut, fără să se scadă întâi CAS, CASS și deducerea personală.
- Se uită de facilitatea pentru salariul minim (200/300 lei), atunci când se aplică, care reduce baza de calcul înainte de aplicarea impozitului.
- Se calculează impozitul înainte de a verifica dacă baza impozabilă rezultată este negativă — în acest caz impozitul este 0, nu o valoare negativă.
- Se citează drept temei legal doar regula generală de 10% pentru venituri, fără a menționa articolul specific veniturilor din salarii, mai direct și mai ușor de verificat.

## Ce face iConta.eu

Motorul de calcul determină baza impozabilă parcurgând, în ordine, scăderea facilității salariului minim (dacă se aplică), a CAS și CASS, apoi a deducerii personale din venitul brut impozabil — cu regula explicită că un rezultat negativ este readus la 0. Impozitul se calculează la cota de 10% pe această bază, plus, separat, impozitul pe eventualele tichete de masă în exces (calculat la cota de 10% pe (nominal − CASS aferentă tichetelor)). Cotele folosite (CAS, CASS, impozit) sunt citite dintr-un registru intern versionat, astfel încât un calcul pentru o lună trecută folosește automat cota valabilă la acea dată.

[iConta.eu](/)
