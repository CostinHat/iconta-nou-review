---
title: Cum reconciliezi registrul mijloacelor fixe cu balanța contabilă?
description: Soldul contului 2813 din balanță trebuie să fie egal, în orice moment, cu suma amortizărilor cumulate calculate în registrul mijloacelor fixe pentru fiecare activ activ — o diferență înseamnă o notă lunară lipsă sau înregistrată greșit.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum reconciliezi registrul mijloacelor fixe cu balanța contabilă?

Registrul de mijloace fixe și balanța contabilă ar trebui să spună întotdeauna aceeași poveste — dar registrul calculează amortizarea teoretic corectă pe fiecare activ, în timp ce balanța reflectă doar ce a fost efectiv înregistrat, lună de lună, prin note contabile. Diferența dintre ele, când apare, arată exact unde a scăpat o notă.

## Temeiul legal

::: ghid-temei
**Art. 28 alin. (1) din Codul fiscal (Legea 227/2015)**: *„Cheltuielile aferente achiziționării, producerii, construirii mijloacelor fixe amortizabile, precum și investițiile efectuate la acestea se recuperează din punct de vedere fiscal prin deducerea amortizării potrivit prevederilor prezentului articol."*

**Art. 28 alin. (12) lit. a)** (momentul de start): *„Amortizarea fiscală se calculează după cum urmează: a) începând cu luna următoare celei în care mijlocul fix amortizabil se pune în funcțiune, prin aplicarea regimului de amortizare prevăzut la alin. (5);"*
:::

Recuperarea fiscală a costului se face lună de lună, prin note contabile efective (6811 = 2813) — nu doar prin calculul teoretic din registru. Soldul contului 2813 din balanță e suma tuturor acestor note deja înregistrate; el trebuie să corespundă, pentru fiecare mijloc fix în parte, cu amortizarea cumulată pe care ar calcula-o registrul la aceeași dată, pornind de la data punerii în funcțiune.

## Cum se face reconcilierea

1. **Se extrage, pentru fiecare mijloc fix din registru**, amortizarea cumulată calculată la data reconcilierii (nu valoarea de intrare, ci amortizatul la zi, pe metoda reală a activului).
2. **Se însumează** aceste valori — totalul trebuie să fie egal cu soldul contului **2813** din balanța de verificare, la aceeași dată.
3. **O diferență** arată una din două situații:
   - **nu s-a înregistrat nota lunară de amortizare** (6811 = 2813) pentru una sau mai multe luni, pentru unul sau mai multe active — soldul din balanță e mai mic decât calculul din registru;
   - **s-a înregistrat o notă manuală incorectă** (sumă greșită, activ greșit, dublare) — soldul din balanță nu corespunde niciunei combinații plauzibile de amortizări lunare corecte.
4. **Se identifică lunile/activele lipsă** comparând, activ cu activ, amortizarea cumulată teoretică (din registru) cu ce a fost efectiv înregistrat pe acel activ în notele contabile — nu la nivel agregat, pentru că două erori de sens opus se pot anula la nivelul totalului.

## Ce se greșește în practică

- **Se reconciliază doar totalul** contului 2813, fără să se coboare pe fiecare activ în parte — o eroare de +500 lei pe un activ și una de −500 lei pe altul dau un total corect, dar ambele active au date greșite.
- **Se compară registrul cu balanța la date diferite** — dacă registrul e calculat „la zi" (data curentă), iar balanța verificată e de la finalul lunii trecute, diferența aparentă vine doar din decalajul de o lună de amortizare, nu dintr-o eroare reală.
- **Se ignoră mijloacele fixe scoase din evidență** în perioada reconciliată — după o casare sau o vânzare, activul nu mai apare în registrul curent, dar soldul lui din 2813 trebuie să fi ieșit corect din balanță prin nota de scoatere din evidență, nu doar „dispărut" din calcul.

## Ce face iConta.eu

Amortizarea se calculează cu un singur motor, folosit deopotrivă de ecranul registrului de mijloace fixe și de generatorul declarației D406/SAF-T — nu există un calcul separat, simplificat, pentru raportare. Registrul arată, pentru fiecare activ, amortizatul și rămasul calculate la zi, pe metoda reală înregistrată pentru acel activ, ceea ce dă un punct de comparație consistent față de soldul efectiv din contul 2813.

[iConta.eu](/)
