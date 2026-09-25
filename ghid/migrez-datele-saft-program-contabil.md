---
title: "Cum migrez datele SAF-T într-un program contabil nou?"
description: "Ce obligație rămâne neschimbată la schimbarea programului de contabilitate: depunerea declarației D406 (SAF-T), conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum migrez datele SAF-T într-un program contabil nou?

**Limitare declarată onest**: procedura tehnică de migrare a datelor contabile istorice dintr-un program în altul (formatul fișierelor de export/import, maparea planurilor de conturi) e o chestiune de compatibilitate software, nu o obligație reglementată de legislația fiscală, așa că nu are un „temei legal" propriu-zis. Ce rămâne reglementat, indiferent de programul folosit, e obligația de raportare SAF-T (declarația D406) — aceasta nu depinde de programul contabil, ci de firma raportoare.

## Temeiul legal

::: ghid-temei
„În vederea stabilirii stării de fapt fiscale și a obligațiilor fiscale datorate, contribuabilul/plătitorul are obligația să conducă evidențe fiscale, potrivit actelor normative în vigoare."
— Legea 207/2015 (Codul de procedură fiscală), art. 108 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce se poate spune cu certitudine, pornind de la acest cadru general:

- Obligația de a conduce evidențe fiscale și de a raporta SAF-T (D406) aparține **firmei**, nu programului software folosit — schimbarea programului de contabilitate nu suspendă și nu resetează această obligație.
- La schimbarea programului, continuitatea evidenței contabile (solduri de deschidere, registrul jurnal, registrul inventar) trebuie asigurată integral în noul program, pentru ca fiecare raportare SAF-T ulterioară să reflecte corect situația reală a firmei, nu doar datele introduse de la data migrării încolo.
- Fișierele SAF-T generate anterior (declarațiile D406 deja depuse) rămân documente oficiale depuse la ANAF, indiferent de programul care le-a generat — ele nu trebuie „refăcute" în noul program, dar datele contabile pe care s-au bazat trebuie să fie regăsibile în evidența firmei pentru perioada de prescripție.
- Nu există, în sursele fiscale disponibile, o procedură specială de „migrare SAF-T între programe" — grija tehnică revine integral firmei/programului contabil ales, cu respectarea obligației generale de evidență corectă și completă.

## Ce se greșește în practică

- Se presupune că simpla existență a fișierelor SAF-T deja depuse la ANAF echivalează cu păstrarea evidenței contabile complete în noul program — de fapt SAF-T e un export structurat pentru raportare, nu un substitut al registrelor contabile obligatorii.
- Se migrează doar soldurile finale, fără detaliile tranzacțiilor din perioada anterioară, ceea ce face imposibilă o eventuală reconciliere sau corectare ulterioară a unei declarații SAF-T deja depuse.
- Se schimbă programul contabil la mijlocul unei perioade de raportare SAF-T fără să se verifice dacă noul program poate genera corect declarația pentru perioada respectivă, cu toate secțiunile cerute de structura oficială.

## Ce face iConta.eu

iConta.eu generează declarația D406 (SAF-T) pe baza datelor contabile introduse și înregistrate direct în aplicație. Pentru o firmă care migrează dintr-un alt program contabil în iConta.eu, continuitatea evidenței (solduri de deschidere, istoricul tranzacțiilor relevante) trebuie asigurată prin introducerea sau importul datelor istorice în aplicație — iConta.eu nu importă automat fișiere SAF-T generate de alte programe ca sursă de populare a propriei evidențe contabile; datele trebuie introduse potrivit fluxurilor de import disponibile în aplicație.

[iConta.eu](/)
