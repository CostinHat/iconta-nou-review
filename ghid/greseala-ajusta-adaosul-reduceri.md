---
title: Greșeala de a nu ajusta adaosul la reduceri
description: Legea cere recalcularea marjei brute la orice schimbare a prețului de vânzare la metoda global-valorică — iConta.eu nu are, deocamdată, un ecran dedicat pentru asta.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeala de a nu ajusta adaosul la reduceri

Când un magazin care ține gestiunea la preț cu amănuntul (metoda global-valorică) reduce prețul de vânzare al unor articole aflate deja în stoc, adaosul comercial evidențiat în contul 378 pentru acele articole nu se ajustează singur — el rămâne la valoarea stabilită la recepție, dacă nimeni nu intervine.

## Temeiul legal

::: ghid-temei
„În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă. În această situație, costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor. Orice modificare a prețului de vânzare presupune recalcularea marjei brute."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (8)
:::

Ultima teză e directă: „orice modificare a prețului de vânzare presupune recalcularea marjei brute." Legea nu face distincție între o majorare și o reducere de preț — orice schimbare a prețului de vânzare la un articol aflat deja în stoc obligă la recalcularea adaosului (marjei brute) aferent, nu doar la momentul intrării în gestiune.

## Ce se greșește în practică

- Se aplică o reducere de preț la raft (etichetă, promoție, lichidare de stoc) fără nicio operațiune contabilă asociată — adaosul înregistrat în 378 pentru articolele respective rămâne cel calculat la prețul vechi.
- Se presupune că diferența se „reglează singură" la următoarea descărcare lunară de gestiune, prin coeficientul K. Nu e adevărat: coeficientul K redistribuie proporțional adaosul existent în sold asupra vânzărilor lunii, dar nu corectează adaosul unui articol anume care a fost repreț­uit — el lucrează la nivel agregat de cont, nu articol cu articol.
- Rezultatul, dacă reducerile sunt frecvente și nu se ajustează adaosul, este un coeficient K din ce în ce mai depărtat de marja comercială reală aplicată efectiv la vânzare.

## Ce face iConta.eu

Motorul de recepție (NIR global-valoric) fixează prețul de vânzare și adaosul aferent doar la momentul intrării în gestiune. Verificarea codului sursă nu a găsit niciun endpoint dedicat de „reprețuire" sau de ajustare a adaosului pe un stoc deja recepționat — deci, la acest moment, iConta.eu nu are un ecran specific pentru recalcularea automată a marjei brute atunci când se schimbă prețul de vânzare al unor articole aflate deja în stoc.

Recalcularea cerută de lege trebuie făcută manual de contabil, printr-o notă de ajustare a adaosului (cont 378), pe baza diferenței reale dintre prețul vechi și cel nou aplicat articolelor în cauză. Această notă manuală trebuie introdusă înainte de descărcarea lunii în care s-a aplicat reducerea, pentru ca și coeficientul K al lunii să reflecte adaosul real.

[iConta.eu](/)
