---
title: D300 precompletat — cum îl verific înainte de depunere?
description: iConta generează propriul decont din facturile firmei, cu gărzi de profil și reconciliere automată pe cotele de TVA — aplicația nu importă și nu compară automat cu nicio sursă externă, verificarea finală rămânând bazată pe evidența contabilă proprie (facturi, jurnale, balanță).
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# D300 precompletat — cum îl verific înainte de depunere?

Decontul D300 generat de aplicație are propriile verificări interne, dar acestea privesc consistența internă a datelor firmei, calculate din facturile deja înregistrate — nu o validare independentă dintr-o sursă externă. Sursele verificate (cod sursă, temei legal) nu confirmă existența unui mecanism ANAF de decont D300 precompletat, disponibil pentru comparație automată; verificarea finală, linie cu linie, rămâne oricum un pas manual al contabilului, bazat pe evidența contabilă proprie.

## Temeiul legal

::: ghid-temei
„19  TOTAL TAXĂ COLECTATĂ (sumă de la rd. 1 până la rd. 18, cu excepţia celor de la rd. 3.1,
5.1, 7.1, 12.1, 12.2)”

„35  TOTAL TAXĂ DEDUSĂ (rd. 31 + rd. 32 + rd. 33 + rd. 34)”
— OPANAF 174/2026, ANEXA 2

„Formularul (300) «Decont de taxă pe valoarea adăugată» se completează de persoanele
impozabile înregistrate în scopuri de TVA conform art. 316 din Legea nr. 227/2015 [...]”
— OPANAF 174/2026
:::

## Ce verificări rulează efectiv înainte de a ajunge la un decont de comparat

Decontul generat de aplicație trece deja prin gărzi de profil (date de identificare complete, pro-rata validă), calculul propriu-zis pe cote, un gard de oglindă pentru taxarea inversă și o reconciliere independentă a totalurilor pe cotele automate — toate rulate pe datele proprii ale firmei, din facturile înregistrate în aplicație.

Aceste verificări confirmă doar consistența internă a decontului generat de aplicație, pe baza propriilor date (facturi, rânduri manuale) — nu o validare independentă dintr-o altă sursă. Nu există în sursele verificate o confirmare a unui mecanism ANAF de propunere precompletată pentru D300 cu care decontul să poată fi comparat automat. Verificarea rămâne, prin urmare, cea internă descrisă mai sus, completată de confruntarea cu evidența contabilă proprie (jurnale, balanță) — mai ales pe rândurile care nu sunt acoperite de reconcilierea automată a aplicației: rândurile manuale (intracomunitar, taxare inversă, ajustări), lanțul de regularizări rd.36–45 și TVA la încasare.

## Ce se greșește în practică

- Se presupune, fără verificare, că decontul generat de aplicație e complet și corect doar pentru că a trecut de gărzile automate, fără o confruntare cu jurnalele/balanța proprie.
- Se compară doar totalurile finale (rd.19, rd.35) fără să se verifice și rândurile individuale unde ar putea apărea diferențe compensate reciproc.
- Nu se verifică dacă toate facturile relevante din perioadă au fost efectiv preluate de aplicație (status finalizat, nu ciornă) înainte de a face comparația.
- Se ignoră rândurile manuale la comparație, deși acestea sunt exact zona neacoperită de reconcilierea automată internă și cea mai predispusă la diferențe.

## Ce face iConta.eu

Aplicația generează decontul strict din propriile date — facturile firmei, preluate pe fereastra fiscală (`pull`), calculate automat pe cote (`calcul_d300`) și verificate printr-o reconciliere a doua cale (`d300_reconciliere.verifica_reconciliere`) care recalculează independent totalurile pe cotele automate 21/11/9%. Sursele verificate nu confirmă existența unui mecanism ANAF de decont D300 precompletat; aplicația nu are, în orice caz, nicio funcționalitate de import sau comparare automată cu o asemenea sursă externă — verificarea finală rămâne un pas manual, bazat pe evidența contabilă proprie, iar zonele cele mai importante de verificat sunt exact cele pe care reconcilierea automată a aplicației nu le acoperă: rândurile manuale, lanțul de regularizări și TVA la încasare.

[iConta.eu](/)
