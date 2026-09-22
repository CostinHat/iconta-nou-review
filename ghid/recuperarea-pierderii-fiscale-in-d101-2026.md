---
title: Cum se reportează pierderea fiscală în D101 2026
description: Pierderea fiscală se reportează la rd. 39.1 din D101, dar numai dacă rd. 38.1 e profit și numai în limita rd. 39, iar plafonul legal de 70% din profitul anului de recuperare (art. 31 alin. 1 Cod fiscal) nu apare verificat nicăieri în instrucțiunile formularului.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se reportează corect pierderea fiscală în D101 pe 2026?

Reportarea pierderii fiscale în D101 trece prin două rânduri — rd. 39 și rd. 39.1 — și două condiții care se aplică simultan: una scrisă explicit în instrucțiunile formularului (recuperi doar dacă anul curent e pe profit, și doar până la suma disponibilă) și una din Codul fiscal, care limitează recuperarea la 70% din profitul anului, indiferent cât de mare e pierderea disponibilă.

## Temeiul legal

::: ghid-temei
**OPANAF 206/2025, rd. 35-40:** *„35 Total profit impozabil/pierdere fiscală pentru anul de raportare, înainte de ajustarea cu pierderile curente (rd. 22 + rd. 34) ... 381 [=38.1] Profit impozabil/pierdere fiscală, înainte de reportarea pierderii din anii precedenţi (rd. 35 + rd. 36 + rd. 37 - rd. 38) ... 39 Pierdere fiscală de recuperat din anii precedenţi ... 391 [=39.1] Pierdere fiscală de recuperat în anul curent ... 40 Profit impozabil aferent anului de raportare (rd. 381 - rd. 391)"*

**OPANAF 206/2025, instrucțiuni rd. 39.1:** *„Rândul 391 se completează cu valoarea pierderii fiscale de recuperat în perioada curentă, potrivit art. 31 din Legea nr. 227/2015... Rândul se completează numai în situaţia în care se declară profit (rândul 381). Suma care se înscrie la acest rând este mai mică sau cel mult egală cu suma înscrisă la rândul 39."*

**CF art. 31 alin. (1)** — plafonul de 70%, pentru pierderi din 2024 încoace: *„Pierderile fiscale anuale stabilite prin declaraţia de impozit pe profit, începând cu anul 2024/anul fiscal modificat care începe în anul 2024, după caz, se recuperează din profiturile impozabile realizate, în limita a 70% inclusiv, în următorii 5 ani consecutivi. Recuperarea pierderilor se va efectua în ordinea înregistrării acestora, la fiecare termen de plată a impozitului pe profit."*

**CF art. 31 alin. (7)** — regimul pierderilor mai vechi de 2024: *„Pierderile fiscale anuale ... aferente anilor precedenţi anului 2024 ... rămase de recuperat la data de 31 decembrie 2023, se recuperează ... în limita a 70% din profiturile impozabile respective, pe perioada rămasă de recuperat din cei 7 ani consecutivi ulteriori anului înregistrării pierderilor respective."*
:::

## Cele două condiții care se aplică simultan

**Condiția din formular** (instrucțiunile rd. 39.1): reportezi pierdere doar dacă anul curent e pe profit (rd. 38.1 pozitiv), și doar până la suma efectiv disponibilă din anii anteriori (rd. 39):

```
rd.39.1 ≤ rd.39
rd.39.1 se completează NUMAI dacă rd.38.1 > 0
rd.40 = rd.38.1 - rd.39.1
```

**Condiția din Codul fiscal** (art. 31 alin. 1): chiar dacă rd. 39 are suficientă pierdere disponibilă, nu poți recupera mai mult de **70% din profitul impozabil al anului** (rd. 38.1). Restul de 30% rămâne impozabil, indiferent cât de mare e pierderea de recuperat.

Cele două condiții nu sunt interschimbabile: instrucțiunile formularului limitează suma la ce ai disponibil (rd. 39), Codul fiscal limitează suma la un procent din profitul anului curent (rd. 38.1). Respecți întotdeauna pe cea mai restrictivă dintre ele.

## Un exemplu

::: ghid-exemplu
O firmă are la 1 ianuarie **200.000 lei** pierdere fiscală de recuperat din anii precedenți (rd. 39), din 2024. În anul curent, profitul înainte de reportare (rd. 38.1) e **120.000 lei**.

- Limita din formular: rd. 39.1 ≤ rd. 39 = 200.000 lei — pierderea disponibilă ar acoperi tot profitul.
- Limita din art. 31 alin. (1): 70% × 120.000 = **84.000 lei** — atât se poate recupera, nu 120.000.

Rd. 39.1 corect = **84.000 lei**, nu 120.000. Rd. 40 (profit impozabil) = 120.000 − 84.000 = **36.000 lei**, impozitat cu 16% = **5.760 lei**. Dacă s-ar fi recuperat toți cei 120.000 lei, impozitul ar fi ieșit zero — greșit, pentru că depășește plafonul de 70%.
:::

## Pentru pierderile mai vechi de 2024

Dacă la 31 decembrie 2023 mai aveai pierdere nerecuperată din ani anteriori lui 2024, ea nu se pierde, dar se supune aceluiași plafon de 70%, pe perioada rămasă din cei 7 ani consecutivi de la anul în care a apărut. Când într-un an recuperezi și pierderi vechi, și pierderi noi (din 2024+), cele două se cumulează pentru aplicarea limitei de 70% — nu sunt plafoane separate.

## Ce se greșește în practică

- **Se recuperează 100% din profitul anului**, atâta timp cât rd. 39 are suficientă pierdere disponibilă. Plafonul legal de 70% din art. 31 alin. (1) se aplică indiferent de câtă pierdere ai acumulată.
- **Se completează rd. 39.1 și când rd. 38.1 e negativ (pierdere)**, deși instrucțiunile spun explicit „numai în situaţia în care se declară profit".
- **Se tratează pierderile vechi (pre-2024) și cele noi ca plafoane separate de 70%**, când de fapt se cumulează pentru aceeași limită.

## Ce face iConta.eu

Rd. 39.1 e verificat față de rd. 39 (nu poți introduce mai mult decât ai disponibil) și e completat doar când rd. 38.1 e profit, exact cum cer instrucțiunile OPANAF 206/2025.

**Plafonul legal de 70% din art. 31 alin. (1) nu e verificat automat** la completarea rd. 39.1 — singura verificare aplicată e față de rd. 39. Când completezi reportul pierderii, calculează manual limita de 70% din profitul anului (rd. 38.1) înainte de a introduce suma.

Vezi și: [pierderea fiscală reportată — plafonul de 70% și termenul de 5 ani](/ghid/pierdere-fiscala-reportata).

[iConta.eu](/)
