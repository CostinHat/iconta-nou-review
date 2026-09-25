---
title: "Cum verific SAF-T cu balanța înainte de depunere?"
description: "De ce fișierul D406/SAF-T trebuie să corespundă exact balanței de verificare a firmei și cum se face verificarea înainte de depunere."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific SAF-T cu balanța înainte de depunere?

Fișierul standard de control fiscal (SAF-T, depus prin Declarația informativă D406) nu e un document separat, inventat pentru ANAF — e o transpunere electronică a aceleiași evidențe contabile din care iese balanța de verificare. Dacă cele două nu se leagă, înseamnă că D406 fie omite tranzacții reale, fie raportează altele decât cele înregistrate în contabilitate, ceea ce e exact ce controlul ANAF va observa primul.

## Temeiul legal

::: ghid-temei
„Orice operațiune economico-financiară efectuată se consemnează în momentul efectuării ei într-un document care stă la baza înregistrărilor în contabilitate, dobândind astfel calitatea de document justificativ.
(2) Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea 82/1991, art. 6 alin. (1), (2) (sursă: anaf_surse/legea_82_1991_consolidat.txt)
:::

Consecința practică pentru SAF-T:

- Obligația de depunere a D406 revine, conform OPANAF 1783/2021, categoriilor largi de contribuabili (societăți pe acțiuni, SRL-uri, SNC, SCS ș.a.), pe grupe de mărime cu termene de referință eșalonate.
- Pentru că raportul dintre documentul justificativ și înregistrarea contabilă e o obligație legală (art. 6), iar SAF-T redă exact aceste înregistrări sub formă de `GeneralLedgerEntries`, un SAF-T care nu se leagă de balanța de rulaje independentă înseamnă o ruptură între ce s-a înregistrat și ce s-a raportat.
- Verificarea de bază e simplă: soldurile finale per cont din SAF-T trebuie să coincidă cu soldurile finale ale acelorași conturi din balanța de verificare a aceleiași perioade, iar totalul debitelor trebuie să fie egal cu totalul creditelor (dubla partidă).

## Ce se greșește în practică

- Se generează SAF-T dintr-o extragere separată de facturi/plăți, diferită de sursa din care se face balanța, iar cele două ajung să diveargă fără ca nimeni să observe până la un control încrucișat.
- Se depune D406 „pe zero" pentru o lună fără mișcări, dar cu tranzacții fabricate sau cu secțiuni goale completate incorect, în loc de un fișier gol, conform structurii reale a lunii.
- Se ignoră dezechilibrul dintre suma debitelor și suma creditelor din SAF-T, presupunând că orice diferență mică „nu contează" — de fapt orice dezechilibru de dublă partidă e un semnal că lipsește o linie sau un cont a fost mapat greșit.

## Ce face iConta.eu

iConta.eu generează D406/SAF-T dintr-o singură sursă: aceleași înregistrări contabile care alimentează și balanța de rulaje. Aplicația are un gard intern care, înainte de a permite generarea declarației, verifică balanța per cont din SAF-T (calculată din `GeneralLedgerEntries`) față de rulajul independent din baza de date și blochează depunerea dacă apare un dezechilibru de dublă partidă sau o diferență de sold pe vreun cont — declarația nu se generează până când sursa contabilă și SAF-T-ul nu coincid. Restul reconcilierilor fine (secțiuni precum `Payments`, `Assets` sau `MovementOfGoods`) sunt tratate separat, pe măsură ce sunt acoperite de aplicație.

[iConta.eu](/)
