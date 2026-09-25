---
title: Diferențe între SAF-T și balanța de verificare
description: Balanța de verificare (art. 22 Legea contabilității nr. 82/1991) e un instrument lunar de control intern al soldurilor; SAF-T/D406 (OPANAF nr. 1783/2021 și nr. 407/2025) e o declarație fiscală structurată, cu granularitate pe tranzacție, transmisă periodic către ANAF.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Diferențe între SAF-T și balanța de verificare

Ambele pornesc din aceleași înregistrări contabile, dar au scop, format și granularitate complet diferite — a le confunda duce la interpretarea greșită a unor discrepanțe care, de fapt, sunt firești.

### Balanța de verificare — control intern, la nivel de sold

Potrivit **art. 22 din Legea contabilității nr. 82/1991**: „Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare." E un document intern, generat din propria evidență contabilă, care listează **soldurile inițiale, rulajele debitoare/creditoare și soldurile finale** ale fiecărui cont sintetic (sau analitic) — un instrument de auto-control, nu o declarație depusă la ANAF.

### SAF-T (D406) — declarație fiscală structurată, la nivel de tranzacție

SAF-T (Standard Audit File for Tax) e fișierul standardizat XML prin care se depune declarația **D406**, reglementată prin **OPANAF nr. 1783/2021** (pentru contribuabilii mari și mijlocii) și **OPANAF nr. 407/2025** (extinderi/actualizări ulterioare ale obligației și structurii). Spre deosebire de balanța de verificare, SAF-T nu se oprește la solduri — conține **tranzacția individuală**: fiecare notă contabilă, cu conturile debitate/creditate, documentul sursă, partenerul (client/furnizor), data și suma.

### De ce apar diferențe aparente între cele două

**1. Nivel de agregare diferit.** Balanța arată un sold pe cont; SAF-T arată tranzacțiile care compun acel sold. O balanță „corectă" la nivel de sold poate ascunde erori de imputare (sumă corectă, cont analitic greșit) pe care abia la nivel de tranzacție din SAF-T le observi — reciproca nu se întâmplă: dacă SAF-T e corect complet, balanța derivată din el trebuie să fie identică cu balanța din contabilitate, pentru că ambele pornesc din același jurnal contabil.

**2. Perioadă de referință diferită.** Balanța de verificare, conform art. 22 din Legea nr. 82/1991, se întocmește **lunar**. Perioada de raportare pentru SAF-T poate diferi ca dată de generare/transmitere de data la care ați rulat ultima balanță — dacă între cele două există înregistrări ulterioare (note de corecție, stornări), balanța „veche" și fișierul SAF-T generat mai târziu nu vor coincide până nu regenerați ambele la aceeași dată de referință.

**3. Reguli de validare structurală proprii SAF-T.** SAF-T impune reguli de completare care nu au corespondent direct într-o balanță clasică (de exemplu, fiecare linie de tranzacție trebuie să aibă fie partener — cod de client/furnizor —, fie un cod propriu „00"+CUI, niciodată ambele lipsă). O balanță poate „ieși" corect valoric fără ca sursa ei (jurnalul contabil) să respecte deja aceste reguli de structură, caz în care generarea SAF-T scoate la iveală probleme pe care balanța, singură, nu le semnalează.

### Cum verificați coerența dintre ele

1. Generați balanța de verificare la exact aceeași dată de referință (ultima zi a lunii/perioadei) la care s-a generat fișierul SAF-T.
2. Comparați soldurile finale pe conturi sintetice din balanță cu totalurile agregate din secțiunea `GeneralLedgerEntries` a fișierului SAF-T — dacă diferă, sursa e fie o operațiune ulterioară generării unuia dintre cele două, fie o eroare de mapare a conturilor la generarea SAF-T.
3. Dacă balanța e corectă dar SAF-T nu se validează structural, problema e de regulă la nivelul liniilor de tranzacție (lipsă partener/cod propriu), nu la nivelul soldurilor — se corectează în sursa datelor, nu prin ajustarea manuală a fișierului XML.

### Ce nu trebuie confundat

Balanța de verificare e un instrument de gestiune internă, fără termen legal de depunere la ANAF; D406/SAF-T e o **declarație fiscală** cu termen de depunere și sancțiuni pentru nedepunere sau depunere eronată, reglementată prin ordinele ANAF menționate mai sus. Discrepanțele dintre ele nu înseamnă automat o eroare contabilă — de cele mai multe ori înseamnă doar că cele două nu au fost generate la aceeași dată de referință.
