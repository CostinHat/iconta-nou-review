---
title: "Ghidul ANAF pentru SAF-T: ce trebuie să citesc"
description: "Actele normative care reglementează obligația SAF-T (D406) — de la obligația de bază din Codul de procedură fiscală la ordinul ANAF cu structura fișierului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ghidul ANAF pentru SAF-T: ce trebuie să citesc

SAF-T nu e reglementat printr-un „ghid" unic, ci prin două acte care se completează: Codul de procedură fiscală stabilește obligația de principiu, iar un ordin ANAF stabilește structura tehnică, procedura de transmitere și termenele concrete.

## Temeiul legal

::: ghid-temei
„(1) Contribuabilul/Plătitorul are obligația de a depune la organul fiscal central o declarație cuprinzând informații din evidența contabilă și fiscală, denumită în continuare fișierul standard de control fiscal.
(2) Fișierul standard de control fiscal se depune în format electronic, la termenul stabilit prin ordin al președintelui A.N.A.F."
— Legea 207/2015 (Codul de procedură fiscală), art. 59^1 alin. (1) și (2) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Pentru un contabil care vrea să înțeleagă exact ce se cere, ordinea de citire recomandată e:

- **Legea 207/2015, art. 59^1**: stabilește obligația de principiu (depunerea unei declarații cu date din evidența contabilă și fiscală) și delegă la ordin ANAF detaliile tehnice — natura informațiilor, modelul de raportare și termenele.
- **OPANAF 1783/2021**: ordinul care pune în aplicare art. 59^1 — conform art. 1, stabilește „natura informațiilor pe care contribuabilul/plătitorul trebuie să le declare prin fișierul standard de control fiscal (SAF-T)"; conform art. 2, precizează că SAF-T se transmite prin **Declarația informativă D406**; conform art. 3-5, stabilește procedura de transmitere, termenele și datele de la care diferitele categorii de contribuabili au devenit obligate.
- **Anexele ordinului**: anexa 1 descrie natura informațiilor (structura SAF-T, bazată pe standardul OECD SAF-T 2.0, adaptat pentru România), anexa 2 e modelul declarației D406, anexa 3 procedura de transmitere, anexa 4 termenele generale de transmitere, iar anexa 5 data/datele de la care fiecare categorie de contribuabili e obligată și categoriile exceptate.
- SAF-T e definit ca „un fișier în format electronic, de tip XML, conținând date extrase" din evidența contabilă și fiscală — nu un raport liber, ci o structură XML strict determinată.
- Pentru corectarea erorilor, Codul de procedură fiscală prevede un regim mai blând dacă fișierul e corectat până la termenul de depunere a următorului SAF-T, sau dacă eroarea provine dintr-un fapt neimputabil contribuabilului.

## Ce se greșește în practică

- Se caută obligația SAF-T doar în ordinul ANAF, ignorând art. 59^1 din Codul de procedură fiscală, care e temeiul legal de bază al obligației — util mai ales când apar modificări ale ordinului fără schimbarea legii.
- Se confundă SAF-T ca „raport" cu D406 ca „declarație" — sunt, de fapt, aceleași lucru: SAF-T e conținutul (fișierul XML), D406 e forma declarativă prin care se transmite.
- Se ignoră anexa 5 (data/datele de la care fiecare categorie de contribuabili e obligată), presupunând că toate firmele au aceleași date de intrare în obligativitate.

## Ce face iConta.eu

iConta.eu generează Declarația informativă D406 (SAF-T) din datele contabile ale firmei — jurnalele de operațiuni, planul de conturi, partenerii, facturile emise/primite, stocurile — structurate conform schemei XSD oficiale ANAF. Aplicația validează structura folosind aceleași reguli ca validatorul oficial ANAF (DUK), inclusiv pentru luni fără mișcări, unde generează o depunere „pe zero" fără a fabrica tranzacții inexistente. Termenul concret de la care fiecare firmă intră în obligativitatea SAF-T rămâne o verificare pe care contabilul o face pe baza anexei 5 a ordinului, pentru categoria din care face parte firma.

[iConta.eu](/)
