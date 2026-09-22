---
title: Ai declarat greșit pierderea fiscală în D101? Cum corectezi și ce se propagă
description: O pierdere fiscală greșită la rd. 38.1/40.1 din D101 nu rămâne izolată în anul respectiv — se propagă în rd. 39 al anilor următori, care o pot recupera doar în limita a 70% din profit, potrivit art. 31 alin. (1) Cod fiscal.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Am declarat greșit pierderea fiscală în D101. Cum corectez și ce efecte are?

O pierdere fiscală greșită la D101 nu e o eroare izolată în anul respectiv. Suma aceea alimentează rd. 39 („pierdere fiscală de recuperat din anii precedenți") în fiecare declarație D101 de după, atâta timp cât pierderea nu e complet consumată. Dacă suma de origine e greșită, toate recuperările ulterioare bazate pe ea sunt greșite la rândul lor — de aceea corectarea nu se oprește la anul în care a apărut eroarea.

## Temeiul legal

::: ghid-temei
**OPANAF 206/2025, rd. 35-40:** *„35 Total profit impozabil/pierdere fiscală pentru anul de raportare, înainte de ajustarea cu pierderile curente (rd. 22 + rd. 34) ... 381 [=38.1] Profit impozabil/pierdere fiscală, înainte de reportarea pierderii din anii precedenţi (rd. 35 + rd. 36 + rd. 37 - rd. 38) ... 39 Pierdere fiscală de recuperat din anii precedenţi ... 391 [=39.1] Pierdere fiscală de recuperat în anul curent ... 40 Profit impozabil aferent anului de raportare (rd. 381 - rd. 391)"*

**OPANAF 206/2025, instrucțiuni rd. 39.1:** *„Rândul 391 se completează cu valoarea pierderii fiscale de recuperat în perioada curentă, potrivit art. 31 din Legea nr. 227/2015... Rândul se completează numai în situaţia în care se declară profit (rândul 381). Suma care se înscrie la acest rând este mai mică sau cel mult egală cu suma înscrisă la rândul 39."*

**CF art. 31 alin. (1)** — limita până la care pierderea se poate recupera an de an: *„Pierderile fiscale anuale stabilite prin declaraţia de impozit pe profit, începând cu anul 2024/anul fiscal modificat care începe în anul 2024, după caz, se recuperează din profiturile impozabile realizate, în limita a 70% inclusiv, în următorii 5 ani consecutivi. Recuperarea pierderilor se va efectua în ordinea înregistrării acestora, la fiecare termen de plată a impozitului pe profit."*
:::

## Ce se corectează și unde se vede

Corecția unei pierderi fiscale greșite se face prin **declarație rectificativă pentru anul de origine** — anul în care pierderea a fost calculată greșit la rd. 38.1/rd. 40.1. Recalculezi lanțul complet:

```
rd.35 (rd.22 + rd.34)
  -> rd.38.1 (rd.35 + rd.36 + rd.37 - rd.38)
  -> dacă rd.38.1 < 0: pierdere fiscală a anului = -rd.38.1
```

Dacă pierderea corectă e diferită de cea inițial declarată, verifici imediat **toți anii ulteriori** în care pierderea respectivă a fost folosită la rd. 39.1 ("pierdere fiscală de recuperat în anul curent"). Fiecare dintre acei ani are propriul rd. 39 ("pierdere de recuperat din anii precedenți") calculat pornind de la suma greșită — deci și acele declarații pot avea nevoie de rectificare, în cascadă, pentru fiecare an în care pierderea de origine a fost efectiv folosită.

## De ce nu se oprește la un singur an

Instrucțiunile OPANAF sunt clare: rd. 39.1 se completează „numai în situaţia în care se declară profit" și suma înscrisă acolo e „mai mică sau cel mult egală" cu rd. 39. Asta înseamnă că valoarea de la rd. 39 dintr-un an ulterior nu e o cifră independentă — e moștenită din pierderea declarată în anii anteriori, redusă cu ce s-a recuperat deja. O eroare la origine circulă mai departe prin acest lanț până când toată pierderea a fost fie recuperată, fie a expirat.

În plus, recuperarea oricărei pierderi — corectă sau nu — e plafonată la 70% din profitul impozabil al anului, pe 5 ani consecutivi (art. 31 alin. 1). Dacă suma corectată e mai mare decât cea inițială, verifici dacă anii care au recuperat deja din ea nu depășesc acum acest plafon.

## Ce se greșește în practică

- **Se corectează doar anul cu eroarea, fără verificarea anilor care au folosit deja pierderea respectivă la rd. 39.1.** Rectificarea unui singur an lasă declarațiile ulterioare cu o bază de recuperare greșită.
- **Se completează rd. 39.1 și în anii cu pierdere, nu doar profit.** Instrucțiunile spun explicit: rândul se completează „numai în situaţia în care se declară profit (rândul 381)".
- **Se recalculează pierderea fără să se verifice plafonul de 70%** din profitul anului de recuperare — o sumă corectată în plus poate depăși plafonul legal în anii care au folosit-o deja.

## Ce face iConta.eu

Lanțul rd. 22 → rd. 35 → rd. 38.1 → rd. 39/39.1 → rd. 40 e calculat conform structurii din OPANAF 206/2025, iar rd. 39.1 respectă condiția din instrucțiuni: nu se completează decât dacă rd. 38.1 e profit, iar suma nu poate depăși rd. 39.

Plafonul de 70% din art. 31 alin. (1) nu e verificat automat de aplicație la completarea rd. 39.1 — valoarea introdusă e verificată doar față de rd. 39, nu față de acest plafon legal. Când corectezi o pierdere, verifică manual dacă recuperarea din anii următori respectă cei 70%.

Vezi și: [pierderea fiscală reportată — plafonul de 70% și termenul de 5 ani](/ghid/pierdere-fiscala-reportata).

[iConta.eu](/)
