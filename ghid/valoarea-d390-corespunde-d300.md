---
title: Ce fac dacă valoarea din D390 nu corespunde cu D300?
description: Aplicația propune un remediu — rectificativă D300 sau corecție D390 — dar decizia și corecția efectivă rămân ale tale, nu se aplică automat.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă valoarea din D390 nu corespunde cu D300?

Când apare un semnal roșu pe comparația D390 ↔ D300, prima reacție utilă e să identifici direcția: e o operațiune declarată în D390 pe care D300 nu o confirmă deloc, sau doar o diferență de cifre pe ambele laturi? Doar prima situație produce roșu — a doua rămâne gri.

## Temeiul legal

::: ghid-temei
**Art. 325 din Codul fiscal (Legea 227/2015)** — obligația declarării lunare, prin declarația recapitulativă, a livrărilor intracomunitare scutite (lit. a) și achizițiilor intracomunitare taxabile (lit. d).

Rectificarea unei declarații deja depuse (fie D390, fie D300) urmează procedura generală de rectificativă, aplicabilă declarațiilor fiscale — corecția rămâne, în toate cazurile, o acțiune confirmată de contribuabil, nu automată.
:::

Un semnal roșu apare specific atunci când D390 arată o valoare pozitivă pe o operațiune (livrare sau achiziție intracomunitară) pe care D300-ul efectiv depus **nu o confirmă deloc** (rândul R1_1 sau R5_1 e zero sau lipsă). Nu apare roșu pentru simpla diferență de cifre între cele două, când ambele au valori pozitive — acolo rămâne gri, tratat ca decalaj legitim.

În situația roșie, aplicația arată explicit cauza (de exemplu „R1_1 absent" pentru o livrare declarată în D390, dar nereflectată în D300) și propune un remediu **sugerat**, nu aplicat automat:

- fie completezi rândul intracomunitar lipsă în D300, prin rectificativă;
- fie corectezi D390, dacă operațiunea a fost raportată greșit la VIES.

Alegerea între cele două variante ține de unde e, de fapt, greșeala — și rămâne decizia ta. Nu există în aplicație o acțiune care aplică automat una dintre corecții.

## Ce se greșește în practică

- Se presupune că bifarea semnalului roșu declanșează o corecție automată — semnalul indică problema și propune direcția, dar rectificativa D300 sau corecția D390 se face separat, ca acțiune deliberată.
- Se corectează D390 din reflex, fără să se verifice mai întâi dacă operațiunea chiar a fost omisă din D300 — uneori D390 e cea greșită (de exemplu raportată la VIES fără acoperire reală), nu D300.
- Se ignoră mesajul explicit al cauzei (de exemplu „R1_1 absent") și se caută diferența pe altă parte a declarației.

## Ce face iConta.eu

Când comparația D390 ↔ D300 produce un roșu, aplicația arată sumele confruntate, rândul afectat (R1_1 sau R5_1) și mesajul cauzei, plus remediul sugerat — rectificativă D300 sau corecție D390, în funcție de unde pare să fie problema. Aplicarea remediului rămâne manuală: nu există o funcție care generează automat o rectificativă sau modifică D390 pe baza acestui semnal.

Pentru diferențele de cifre fără operațiune complet lipsă (ambele rânduri pozitive, dar diferite), starea rămâne gri, cu explicația că poate fi decalaj de exigibilitate, regularizare sau rotunjire — nu se ridică automat la roșu doar pentru o diferență numerică.

[iConta.eu](/)
