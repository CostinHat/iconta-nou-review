---
title: "Cum verific statusul declarației D406 în SPV?"
description: "Mecanismul oficial de confirmare a depunerii D406 (SAF-T) — recipisa, mesajele din Spațiul Privat Virtual și verificarea directă pe portalul ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific statusul declarației D406 în SPV?

După încărcarea fișierului SAF-T în portalul ANAF, apare aceeași întrebare ca la orice declarație: a fost primită corect, sau conține erori care blochează validarea? Procedura de verificare a statusului e descrisă explicit în ordinul care reglementează D406.

## Temeiul legal

::: ghid-temei
„22. În urma încărcării Declaraţiei informative D406, în portalul Agenţiei Naţionale de Administrare Fiscală, documentul este verificat şi analizat, iar în cazul în care contribuabilul/plătitorul este înregistrat în Spaţiul Privat Virtual (SPV), acesta poate primi eventuale mesaje de validare, eroare, atenţionare în secţiunea «Mesaje». 23. Recipisa şi informaţiile despre procesarea Declaraţiei informative D406 sunt transmise în mod automat de către Agenţia Naţională de Administrare Fiscală contribuabilului/plătitorul înscris în SPV [...]. Alternativ, contribuabilii/plătitorii pot verifica stadiul şi rezultatele procesării folosind indexul de încărcare prin interogare directă pe site-ul Agenţiei Naţionale de Administrare Fiscală."
— OPANAF nr. 1.783/2021, Anexa 5 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Ce rezultă practic din text:

- Există **două căi** oficiale de verificare a statusului: mesajele automate primite în secțiunea „Mesaje" din SPV (dacă firma e înregistrată acolo) și interogarea directă pe site-ul ANAF, folosind **indexul de încărcare** primit la depunere — a doua variantă nu depinde de înregistrarea în SPV.
- Documentul emis la finalul procesării e **recipisa** — fișierul care confirmă fie că declarația a fost depusă corect și la termen, fie că a fost depusă cu erori care trebuie corectate.
- Când D406 se depune prin **mai multe fișiere** pentru aceeași perioadă (situație posibilă la volum mare de date), fiecare fișier primește propria recipisă, dar **confirmarea finală** că declarația în ansamblu e conformă apare abia în **ultima recipisă** din serie — recipisele intermediare nu garantează, singure, că întreaga declarație a fost acceptată.
- Dacă recipisa semnalează erori, contribuabilul e responsabil să corecteze fișierul XML și să retransmită declarația, reluând pașii de generare și încărcare descriși de procedură.

## Ce se greșește în practică

- Se consideră declarația depusă cu succes doar pe baza confirmării de încărcare (upload reușit), fără să se aștepte și să se verifice recipisa de procesare, care poate semnala erori ulterioare încărcării.
- La depunerea în mai multe fișiere, se verifică doar prima recipisă primită și se presupune că declarația e completă, deși confirmarea finală vine abia odată cu ultima recipisă din serie.
- Se ignoră varianta de interogare directă pe site-ul ANAF (prin indexul de încărcare), utilă mai ales când firma nu e înregistrată încă în SPV sau mesajele automate întârzie.

## Ce face iConta.eu

La data acestui ghid, iConta.eu generează fișierul D406 pe baza datelor contabile ale firmei, dar depunerea efectivă pe portalul ANAF și urmărirea recipisei/statusului de procesare se fac în afara aplicației, direct pe portalul ANAF sau prin SPV — iConta.eu nu automatizează încă interogarea statusului declarației după depunere.

[iConta.eu](/)
