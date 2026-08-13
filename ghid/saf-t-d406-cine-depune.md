---
title: Declarația SAF-T (D406): ce este, cine depune și de când
description: Ce este fișierul standard de control fiscal SAF-T, cine are obligația să depună D406 potrivit OPANAF 1783/2021 și 407/2025, de la ce dată pe fiecare categorie și ce periodicitate se aplică.
published: 2026-08-13
modified: 2026-08-13
---

# Ce este declarația SAF-T (D406), cine o depune și de la ce dată?

SAF-T nu e o declarație obișnuită. Celelalte raportează totaluri; SAF-T trimite la ANAF **evidența contabilă însăși** — fiecare factură cu liniile ei, planul de conturi, jurnalele, partenerii, plățile. Este fișierul standard de control fiscal, iar de la 1 ianuarie 2025 obligația s-a extins la ultima categorie de contribuabili: cei mici. Dacă firma ta ține contabilitate în partidă dublă, aproape sigur ești obligat.

## Temeiul legal

::: ghid-temei
**OPANAF nr. 1783/2021** — ordinul care a introdus **Declarația informativă D406 „Fișier standard de control fiscal"**, structura ei și termenele de depunere. Schema tehnică este publicată de ANAF ca **schemă XSD**, alături de un ghid al contribuabilului și de nomenclatoarele obligatorii.

**OPANAF nr. 407/2025** — actul care stabilește **categoriile de contribuabili obligați** și calendarul pe categorii. Potrivit acestuia, obligația de depunere revine persoanelor juridice care conduc contabilitatea **în partidă dublă**: societăți (SRL, SA, SCA, SCS, SNC), regii autonome, institute naționale de cercetare-dezvoltare, societăți cooperative, sedii permanente ale nerezidenților, asociații cu și fără scop patrimonial care conduc partidă dublă, precum și nerezidenții înregistrați în scopuri de TVA în România.

**Excluse** de la obligație: persoanele fizice autorizate (PFA), întreprinderile individuale și familiale, persoanele fizice care desfășoară profesii liberale reglementate special, instituțiile publice, entitățile cu activitate suspendată și cele care conduc contabilitatea **în partidă simplă**.

Pentru contribuabilii încadrați la categoria **mici**, obligația se aplică începând cu **1 ianuarie 2025**.
:::

## Regula concretă

**Cine depune.** Criteriul de bază este simplu: dacă ții contabilitate în **partidă dublă** și ești persoană juridică, ești obligat. Un SRL, oricât de mic, intră. Un PFA în partidă simplă nu.

**De când.** Calendarul a fost eșalonat pe categorii de contribuabili, ultima fiind cea a contribuabililor mici, de la 1 ianuarie 2025. Astăzi, practic, toți cei vizați sunt intrați în obligație.

**Ce periodicitate.** Fișierul se depune **lunar sau trimestrial**, urmând aceeași periodicitate ca decontul de TVA. O firmă cu decont lunar depune SAF-T lunar; una cu decont trimestrial, trimestrial. Cine nu e înregistrat în scopuri de TVA depune trimestrial.

Peste raportarea periodică există și două raportări cu ritm propriu:
- **Secțiunea Active** — anual
- **Secțiunea Stocuri** — doar la cererea expresă a ANAF

**Termenul.** Ultima zi calendaristică a lunii următoare perioadei de raportare. Pentru luna ianuarie, termenul e 28 februarie; pentru trimestrul I, 30 aprilie.

**Perioada de grație.** ANAF a prevăzut o perioadă în care depunerea cu întârziere nu se sancționează, calculată de la prima obligație a fiecărui contribuabil. Ea nu anulează obligația — doar amână sancțiunea.

## Un exemplu

::: ghid-exemplu
**SC Exemplu SRL**, contribuabil mic, plătitor de TVA cu decont lunar.

- **Obligația începe:** 1 ianuarie 2025, prima raportare fiind pentru luna ianuarie 2025.
- **Periodicitate:** lunară, pentru că decontul de TVA e lunar.
- **Termenul pentru luna martie 2026:** 30 aprilie 2026.
- **Secțiunea Active:** o raportare anuală separată, la termenul stabilit pentru active.
- **Secțiunea Stocuri:** nu se depune din oficiu — doar dacă ANAF o cere expres.

**Aceeași firmă, dacă ar fi avut decont trimestrial:** ar fi depus SAF-T trimestrial, cu termen 30 aprilie pentru trimestrul I. Periodicitatea nu se alege — vine din vectorul fiscal.
:::

## Ce se greșește în practică

- **Se crede că firmele mici sunt exceptate.** Nu sunt. Criteriul e partida dublă, nu mărimea. Un SRL cu doi angajați și trei facturi pe lună are aceeași obligație ca unul mare.
- **Se confundă cu decontul de TVA.** SAF-T nu raportează totaluri, ci evidența în detaliu: fiecare linie de factură, fiecare cont, fiecare partener. E o categorie diferită de raportare.
- **Se ratează periodicitatea.** Ritmul SAF-T urmează decontul de TVA. O schimbare de perioadă fiscală la TVA schimbă și ritmul SAF-T.
- **Se confundă perioada de grație cu o amânare a obligației.** Fișierul tot trebuie depus; doar sancțiunea pentru întârziere e suspendată temporar.
- **Se lasă pe ultima zi.** Fișierul SAF-T e mare și complex. Prima generare scoate la iveală lipsuri în evidență — conturi nemapate, parteneri fără cod fiscal, unități de măsură absente. Toate cer timp de reparat.

## Ce face iConta.eu

iConta.eu generează fișierul D406 direct din evidența contabilă, cu **liniile reale de factură** — fiecare produs cu cantitatea, unitatea de măsură și prețul lui, nu o linie sintetică pe factură — reconciliate cu antetul. Fișierul se validează pe **validatorul oficial ANAF (DUKIntegrator)** înainte să ajungă la tine.

Nomenclatoarele obligatorii — conturi, unități de măsură, țări, tipuri de document — sunt mapate automat, iar identitatea partenerilor se emite în formatul cerut de schema oficială.

**Două limite, spuse direct:**

Secțiunea **Payments** nu se emite: modelul de date nu conține încă sursa de plăți. Fișierul e valid și acceptat de validator pe zero plăți, dar e incomplet pentru o firmă care are încasări și plăți de raportat.

**Contul pe linia de factură** e cel generic — 707 la vânzare, 371 la stoc — nu contul real pe fiecare produs.

Amândouă sunt în lucru. Până atunci, le știi înainte să depui, nu după.

Depunerea o faci din SPV, cu fișierul deja verificat.

Vezi și: [decontul de TVA și rezultatul perioadei](/ghid/decont-tva-d300-rezultat), care dă periodicitatea SAF-T, și [D394 și reconcilierea cu decontul](/ghid/d394-ce-declari-reconciliere).

[iConta.eu](/)
