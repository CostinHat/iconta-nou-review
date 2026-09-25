---
title: "Cum se impozitează un SRL în primul an de activitate?"
description: "Condițiile în care o firmă nou-înființată poate opta pentru impozitul pe veniturile microîntreprinderilor chiar din primul an fiscal, conform Codului fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se impozitează un SRL în primul an de activitate?

Un SRL nou-înființat nu e obligat automat la impozit pe profit (16%) doar pentru că e la început de drum — poate opta pentru impozitul pe veniturile microîntreprinderilor (cota redusă, aplicată la cifra de afaceri) chiar din primul an fiscal, dacă îndeplinește anumite condiții la data înregistrării la Registrul Comerțului și în cele 90 de zile care urmează.

## Temeiul legal

::: ghid-temei
„(3) O persoană juridică română care este nou-înființată poate opta să plătească impozit pe veniturile microîntreprinderilor începând cu primul an fiscal, dacă condițiile prevăzute la art. 47 alin. (1) lit. d) și h) sunt îndeplinite la data înregistrării în registrul comerțului, iar cea prevăzută la lit. g) în termen de 90 de zile inclusiv de la data înregistrării persoanei juridice respective. În cazul în care, în acest termen, nu se îndeplinește condiția de la art. 47 alin. (1) lit. g), microîntreprinderea datorează impozit pe profit începând cu trimestrul următor celui în care expiră perioada de 90 de zile."
— Legea nr. 227/2015 privind Codul fiscal, art. 48 alin. (3) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Condițiile trimise de art. 48 alin. (3) la art. 47 alin. (1) sunt:

- **lit. d)** — capitalul social e deținut de alte persoane decât statul și unitățile administrativ-teritoriale; trebuie îndeplinită **la data înregistrării** în registrul comerțului.
- **lit. h)** — asociații/acționarii care dețin peste 25% din titlurile de participare/drepturile de vot au desemnat firma respectivă ca singura prin care aplică regimul microîntreprinderilor; trebuie îndeplinită tot **la data înregistrării**.
- **lit. g)** — firma are cel puțin un salariat; această condiție are un termen de grație — trebuie îndeplinită în cel mult **90 de zile de la data înregistrării**, nu neapărat din prima zi.

Dacă în cele 90 de zile firma tot nu are niciun salariat, consecința nu e retroactivă: firma **datorează impozit pe profit începând cu trimestrul următor** celui în care expiră cele 90 de zile — nu de la înființare.

## Ce se greșește în practică

- Se presupune că o firmă nou-înființată e automat microîntreprindere din prima zi, fără verificarea condițiilor de la art. 47 alin. (1) lit. d) și h) chiar la momentul înregistrării — dacă acestea nu sunt îndeplinite la înregistrare, opțiunea pentru micro din primul an fiscal nu mai e posibilă.
- Se ignoră termenul de 90 de zile pentru angajarea primului salariat, presupunând că firma poate rămâne la infinit fără angajat și totuși microîntreprindere — depășirea termenului mută firma la impozit pe profit, nu retroactiv, ci de la trimestrul următor expirării termenului.
- Se confundă condiția de plafon de venituri (100.000 euro, art. 47 alin. 1 lit. c) — care se verifică la 31 decembrie a anului fiscal precedent, deci nu se aplică unei firme din primul ei an — cu obligația de a avea salariat, care e specifică firmelor nou-înființate și are termenul propriu de 90 de zile.

## Ce face iConta.eu

iConta.eu are o funcționalitate reală pentru gestionarea vectorului fiscal al firmei (`core/vector_fiscal_api.py`), care determină ce tip de declarații generează aplicația (D100 pentru profit/microîntreprinderi etc.), pe baza regimului de impozitare configurat pentru firmă. Ce nu automatizează astăzi aplicația: verificarea condițiilor specifice firmelor nou-înființate din art. 48 alin. (3) — inclusiv urmărirea termenului de 90 de zile pentru angajarea primului salariat și trecerea automată la impozit pe profit dacă acest termen e depășit. Încadrarea inițială și verificarea condițiilor rămân, la această dată, o decizie și o verificare manuală a contabilului, introdusă apoi ca regim de impozitare în profilul firmei.

[iConta.eu](/)
