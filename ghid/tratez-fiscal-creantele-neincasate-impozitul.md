---
title: "Cum tratez fiscal creanțele neîncasate la impozitul pe profit?"
description: "La impozitul pe profit, o creanță neîncasată trece prin ajustare (30% peste 270 de zile, sau 100% la faliment/insolvență) și, dacă se scoate din evidență, printr-un al doilea test de deductibilitate, separat."
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez fiscal creanțele neîncasate la impozitul pe profit?

La impozitul pe profit, tratamentul unei creanțe neîncasate parcurge două etape distincte: cât timp creanța rămâne în evidență, se constituie o ajustare pentru depreciere, deductibilă condiționat; dacă și când creanța e scoasă definitiv din evidență, pierderea rămasă trece printr-un al doilea test de deductibilitate, separat de primul.

## Temeiul legal

::: ghid-temei
„Contribuabilul are dreptul la deducerea rezervelor și provizioanelor/ajustărilor pentru depreciere, numai în conformitate cu prezentul articol, astfel: [...] c) ajustările pentru deprecierea creanțelor [...] în limita unui procent de 30% din valoarea acestor ajustări [...] dacă creanțele îndeplinesc cumulativ următoarele condiții: 1. sunt neîncasate într-o perioadă ce depășește 270 de zile de la data scadenței; 2. nu sunt garantate de altă persoană; 3. sunt datorate de o persoană care nu este persoană afiliată contribuabilului."

*(Codul fiscal — Legea nr. 227/2015, art. 26 alin. (1) lit. c))*
:::

## Etapa 1 — ajustarea, cât timp creanța e în evidență

- **Garantată sau la un afiliat** → 0%, indiferent de vechime.
- **Debitor în faliment declarat/insolvență** → 100% (art. 26 alin. (1) lit. j)), imediat, fără prag de zile.
- **Altfel, peste 270 de zile de la scadență** → 30% (art. 26 alin. (1) lit. c)).
- **Sub 270 de zile, fără faliment** → 0%, deocamdată.

## Etapa 2 — pierderea, dacă și când creanța e scoasă din evidență

Partea neacoperită de ajustarea dedusă anterior e deductibilă doar dacă situația se încadrează în una din cele șase excepții de la art. 25 alin. (4) lit. h) — reorganizare confirmată prin hotărâre, faliment închis prin hotărâre, decesul debitorului fără moștenitori recuperabili, dizolvare/lichidare fără succesor, dificultăți financiare majore ale debitorului sau existența unui contract de asigurare. În afara acestor situații, pierderea la scoaterea din evidență rămâne nedeductibilă.

## Ce se greșește în practică

- Se tratează cele două etape ca una singură, deducând integral pierderea de îndată ce creanța devine „veche", fără să se mai verifice condițiile fiecărei etape separat.
- Se aplică pragul de 270 de zile și la debitori aflați deja în faliment declarat, unde deducerea corectă e 100%, imediată.
- Se deduce pierderea la scoaterea din evidență fără verificarea celor șase excepții de la art. 25 alin. (4) lit. h).

## Ce face iConta.eu

`core/provizioane.py` calculează Etapa 1 — `deductibilitate_creanta` întoarce procentul corect (0%/30%/100%) și generează nota `6814=491`. Etapa 2 (scoaterea din evidență și verificarea celor șase excepții) nu e modelată de motor — rămâne o evaluare și o notă contabilă separate, introduse manual de contabil.

[iConta.eu](/)
