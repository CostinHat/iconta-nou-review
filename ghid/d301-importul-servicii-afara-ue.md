---
title: "D301 pentru importul de servicii din afara UE"
description: "Ce secțiune din decontul special D301 se completează pentru serviciile primite de la prestatori stabiliți în afara Uniunii Europene, conform instrucțiunilor OPANAF 592/2016."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# D301 pentru importul de servicii din afara UE

Un serviciu primit de la un prestator dintr-o țară din afara Uniunii Europene, taxabil în România prin taxare inversă, se declară în D301 — dar în altă secțiune decât cea folosită pentru serviciile intracomunitare. Confuzia dintre cele două secțiuni e sursa cea mai frecventă de eroare.

## Temeiul legal

::: ghid-temei
„Secțiunea 4 «Operațiuni prevăzute la art. 307 alin. (2), (3), (5) și (6) din Codul fiscal» se completează de către: - persoanele impozabile obligate la plata taxei conform art. 307 alin. (2) din Codul fiscal, care nu sunt înregistrate și nu trebuie să se înregistreze conform art. 316 din Codul fiscal [...] care sunt beneficiare ale serviciilor care au locul prestării în România conform art. 278 alin. (2) din Codul fiscal și care sunt furnizate de către persoane impozabile care nu sunt stabilite pe teritoriul României [...]
Secțiunea 4.1 «Achiziții de servicii intracomunitare, pentru care beneficiarul este obligat la plata TVA conform art. 307 alin. (2) din Codul fiscal» se completează de către [...] persoanele [...] beneficiare ale serviciilor care au locul prestării în România conform art. 278 alin. (2) din Codul fiscal și care sunt furnizate de către persoane impozabile care nu sunt stabilite pe teritoriul României [...] dar care sunt stabilite în Comunitate [...]"
— OPANAF 592/2016, Anexa 2 — Instrucțiuni de completare a formularului 301 (sursă: anaf_surse/opanaf_592_2016_d301.txt)
:::

Distincția pe care instrucțiunile o fac explicit:

- **Secțiunea 4** e secțiunea generală, pentru toate serviciile taxabile în România prin taxare inversă (art. 307 alin. (2)), primite de la orice prestator nestabilit pe teritoriul României — **indiferent dacă prestatorul e din UE sau din afara ei**.
- **Secțiunea 4.1** e o subdiviziune specifică, dedicată **exclusiv serviciilor de la prestatori stabiliți în Comunitate** (UE) — folosită pentru reconcilierea cu declarația recapitulativă VIES a partenerului din alt stat membru.
- Consecința practică: un **serviciu primit de la un prestator din afara UE** (SUA, Marea Britanie ca stat terț, Elveția etc.) se raportează în **Secțiunea 4**, dar **nu** și în Secțiunea 4.1, care rămâne rezervată strict operațiunilor intracomunitare.
- Această structură există tocmai pentru evitarea neconcordanțelor dintre D301 și D390: doar operațiunile intracomunitare trebuie să se regăsească în ambele declarații, cele cu prestatori din afara UE apar doar în decontul special.

## Ce se greșește în practică

- Se completează Secțiunea 4.1 pentru orice serviciu extern, inclusiv de la prestatori din afara UE, ceea ce creează o neconcordanță artificială la reconcilierea cu D390 (care nu are corespondent pentru state terțe).
- Se omite complet declararea în D301 a unui serviciu de la un prestator dintr-o țară terță, sub presupunerea greșită că „taxarea inversă e doar pentru UE" — art. 307 alin. (2) nu face această distincție, se aplică oricărui prestator nestabilit în România.
- Se confundă noțiunea de „stat membru" cu cea de „stat din afara UE" pentru Marea Britanie, fără verificarea statutului ei curent (stat terț, cu tratament diferit de un stat membru UE).

## Ce face iConta.eu

Modulul D301 al iConta.eu (`core/d301.py`) tratează explicit distincția din OPANAF 592/2016: tipul de operațiune „4" corespunde serviciilor generale prevăzute la art. 307 alin. (2), (3), (5) și (6) — categoria care include și prestatorii din afara UE — iar tipul „5" corespunde specific achizițiilor de servicii intracomunitare, care apar automat atât în Secțiunea 4, cât și ca detaliu în Secțiunea 4.1 (regula de „rollup" S4.1→S4 din instrucțiuni e implementată ca atare, cu comentariu explicit la sursă). Alegerea între tip „4" (serviciu extra-UE) și tip „5" (serviciu intracomunitar) rămâne însă o clasificare pe care contabilul o face la introducerea operațiunii, în funcție de țara reală a prestatorului — aplicația nu deduce ea însăși, din alte date, dacă un partener e stabilit în UE sau într-un stat terț.

[iConta.eu](/)
