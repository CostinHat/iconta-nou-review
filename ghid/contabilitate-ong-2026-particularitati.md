---
title: "Contabilitate ONG 2026: particularități"
description: "Cum diferă contabilitatea unui ONG de cea a unei societăți obișnuite: conturile din grupa 73, evidența separată pe cele două activități și calculul scutirii de impozit pe profit."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Contabilitate ONG 2026: particularități

Contabilitatea unui ONG (asociație, fundație) urmează în linii mari reglementările generale, dar are câteva particularități care nu au echivalent la o societate comercială: un plan de conturi separat pentru veniturile fără scop patrimonial, obligația de a ține evidența distinctă a celor două tipuri de activitate și un regim fiscal cu scutire plafonată pentru partea economică.

## Temeiul legal

::: ghid-temei
„73 VENITURI DIN ACTIVITĂŢILE FĂRĂ SCOP PATRIMONIAL
731 Venituri din cotizaţiile membrilor, contribuţiile băneşti sau în natură ale membrilor şi simpatizanţilor, din cote-părţi primite potrivit statutului [...]
732 Venituri din taxele de înregistrare stabilite potrivit legislaţiei în vigoare
733 Venituri din donaţii, sume sau bunuri primite prin sponsorizare şi ajutoare [...]
734 Venituri financiare rezultate din activităţile fără scop patrimonial [...]
735 Venituri pentru care se datorează impozit pe spectacole
736 Venituri din subvenţii de exploatare [...]
737 Venituri din acţiuni ocazionale, utilizate în scop social sau profesional, potrivit statutului de organizare şi funcţionare
738 Alte venituri din activităţile fără scop patrimonial [...]"
— OMFP 3103/2017, planul de conturi, grupa 73 (sursă: anaf_surse/omfp_3103_2017.txt)
:::

- Veniturile fără scop patrimonial (cotizații, donații, sponsorizări, fonduri publice, acțiuni ocazionale) se înregistrează pe conturile din grupa **73**, defalcate pe natura lor, nu pe conturile generale de venituri 70x-76x folosite de societățile comerciale.
- Veniturile din activitatea economică (dacă organizația desfășoară una) se țin pe conturile obișnuite 70x-76x din OMFP 1802/2014, ca la orice altă entitate.
- Evidența trebuie ținută **distinct** pe cele două categorii de activitate, pentru că fiecare are un regim fiscal diferit la calculul rezultatului fiscal (art. 15 alin. 2-3 din Codul fiscal — venituri neimpozabile versus venituri economice scutite plafonat).
- Cota de impozit pe profit aplicabilă părții economice care depășește plafonul de scutire este de 16% (art. 17 Cod fiscal).

## Ce se greșește în practică

- Se folosesc conturile de venituri generale (70x) și pentru cotizații sau donații, în loc de conturile din grupa 73 — face imposibilă reconstituirea corectă a bazei neimpozabile de la art. 15 alin. (2).
- Se ține o singură evidență de rezultat pentru ambele activități, deși legea cere separarea lor pentru calculul corect al impozitului pe profit datorat.
- Se presupune că toate cele opt conturi din grupa 73 (731-738) au aceeași relevanță fiscală — de fapt fiecare corespunde unei categorii distincte de la art. 15 alin. (2), iar cursul valutar folosit la calculul plafonului de 15.000 EUR trebuie să fie cursul mediu anual comunicat de BNR, nu cursul de la 31 decembrie.

## Ce face iConta.eu

Din ecranul „Operațiuni speciale" → „Operațiuni ONG (OMFP 3103/2017)", iConta.eu generează astăzi nota contabilă pentru cinci din cele opt tipuri de venit fără scop patrimonial: cotizație și contribuție (cont 731), donație și sponsorizare primită (cont 733) și venit financiar (cont 734); celelalte trei categorii din grupa 73 (fonduri publice/finanțări nerambursabile, acțiuni ocazionale, alte venituri AFSP) nu au încă un câmp în formularul din ecran. Aplicația oferă separat un calculator pentru plafonul de scutire de la alin. (3), disponibil momentan doar printr-un apel API, nu din interfață. **iConta.eu nu automatizează încă** o separare completă a rezultatului contabil pe cele două activități (fără scop patrimonial vs. economică) — clasifică veniturile pe conturile corecte din grupa 73 și calculează, la cerere, plafonul de scutire, dar închiderea distinctă a exercițiului pe cele două categorii rămâne în sarcina contabilului.

[iConta.eu](/)
