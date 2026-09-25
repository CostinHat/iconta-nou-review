---
title: "Cum verific decontul precompletat e-TVA"
description: "Ce este decontul precompletat RO e-TVA, ce valoare juridică are și ce obligație de verificare revine persoanei impozabile, conform OUG 70/2024."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum verific decontul precompletat e-TVA

Decontul precompletat RO e-TVA nu e decontul de TVA pe care firma îl depune — e un document de comparație, generat de ANAF din datele deja aflate în sistemele sale (e-Factura, e-Transport, case de marcat, SAF-T), pe care persoana impozabilă are obligația să-l verifice față de propria evidență, nu să-l accepte necondiționat.

## Temeiul legal

::: ghid-temei
„(1) Decontul precompletat RO e-TVA se implementează cu data de 1 august 2024 pentru operațiunile efectuate începând cu data de 1 iulie 2024 de persoanele impozabile înregistrate în scopuri de TVA. (2) Decontul precompletat RO e-TVA se transmite, pentru fiecare perioadă fiscală de raportare, persoanelor impozabile înregistrate în scopuri de TVA, prin mijloace electronice, până la data de 5 inclusiv a lunii următoare termenului legal de depunere a decontului de taxă pe valoarea adăugată. [...] (5) Decontul precompletat RO e-TVA nu constituie titlu de creanță în sensul Legii nr. 207/2015, cu modificările și completările ulterioare. (6) După primirea decontului precompletat RO e-TVA, persoanele impozabile înregistrate în scopuri de TVA verifică datele și informațiile precompletate în concordanță cu operațiunile impozabile realizate și starea de fapt fiscală."
— OUG 70/2024, art. 3 alin. (1), (2), (5) și (6) (sursă: anaf_surse/oug_70_2024_ro_etva_decont_precompletat.txt)
:::

Ce trebuie știut înainte de a folosi acest instrument:

- Decontul precompletat **nu e o obligație de plată** — art. 3 alin. (5) spune explicit că nu constituie titlu de creanță. E un instrument de comparație, nu un act cu forță executorie prin el însuși.
- Firma primește decontul precompletat prin mijloace electronice **până la data de 5** a lunii următoare termenului de depunere a decontului de TVA — deci după ce decontul propriu a fost deja depus, nu înainte, ceea ce înseamnă că verificarea servește mai degrabă la identificarea din timp a unor diferențe pentru perioada următoare.
- Sursele de date pentru precompletare sunt sistemele naționale deja existente — RO e-Factura, RO e-Transport, RO e-Sigiliu, RO e-SAF-T, casele de marcat electronice — deci acoperă doar operațiunile care au trecut prin aceste canale; rubricile pentru care nu există date rămân necompletate.
- Diferențele dintre decontul precompletat și decontul de TVA efectiv depus sunt identificate de ANAF prin Modulul de valorificare RO e-TVA (art. 4 alin. (1)) și pot declanșa notificări de conformare sau, ulterior, acțiuni de control.

## Ce se greșește în practică

- Se tratează decontul precompletat ca fiind "decontul corect" impus de ANAF, deși legea îi neagă explicit calitatea de titlu de creanță — diferențele nu înseamnă automat că firma a greșit.
- Se ignoră faptul că sistemul precompletează doar din sursele de date deja disponibile la ANAF — o operațiune reală, dar netransmisă corect prin e-Factura sau alt sistem sursă, nu apare deloc în precompletare, ceea ce nu înseamnă că nu există obligația de a o declara.
- Se confundă verificarea decontului precompletat cu depunerea decontului de TVA propriu-zis — sunt documente și termene diferite, chiar dacă ambele poartă numele "e-TVA".

## Ce face iConta.eu

iConta.eu generează decontul de TVA (D300) pe baza operațiunilor înregistrate direct în aplicație — facturi emise și primite, jurnal de TVA. La data acestui ghid, iConta.eu nu descarcă și nu compară automat decontul precompletat RO e-TVA transmis de ANAF cu decontul propriu generat, astfel încât verificarea diferențelor dintre cele două rămâne o operațiune separată, făcută de contabil direct în SPV.

[iConta.eu](/)
