---
title: "Ce reconcilieri fiscale ar trebui făcute înainte de fiecare închidere de lună?"
description: Trei reconcilieri contează la fiecare închidere lunară — echilibrul contabil, TVA pe conturi vs decont, și starea notelor (validate vs ciornă). Fiecare cu toleranța și limita ei reală, nu presupusă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce reconcilieri fiscale ar trebui făcute înainte de fiecare închidere de lună?

Trei verificări merită făcute sistematic la fiecare închidere de lună, nu doar la control sau la închiderea anului. Fiecare are o toleranță și o limită declarată — le trecem pe rând.

## Temeiul legal

::: ghid-temei
„Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare." — Legea contabilității nr. 82/1991, art. 22.
:::

## 1. Echilibrul contabil al lunii

Patru verificări separate, combinate într-un verdict unic: notă neechilibrată (debit ≠ credit pe o notă), ledger dezechilibrat (linie ruptă pe perioada brută), linii orfane (fără notă-mamă) și solduri inițiale dezechilibrate. Verificarea de ledger acoperă **doar notele validate** — dacă la închiderea lunii mai sunt note în ciornă, o eroare structurală în ele nu apare încă.

## 2. TVA pe conturi vs decont

Contul 4427 (TVA colectată) se compară cu rândul de colectată din decont; 4426 (deductibilă) cu rândul de deductibilă; rezultatul decontului — de plată sau de recuperat — cu rândurile corespunzătoare. Toleranța acceptată e de 1 leu, pentru că decontul rotunjește la leu iar contabilitatea ține sume cu bani.

O coincidență perfectă (0 = 0) nu înseamnă automat „totul e în regulă" dacă în fereastra verificată există facturi necontabilizate — situația devine un semnal gri, cu zona de necunoaștere numită explicit, tocmai ca să nu se confunde absența ambilor termeni cu o reconciliere reușită.

## 3. Starea notelor: validate vs ciornă

Multe verificări (echilibru pe perioadă, TVA pe conturi) iau în calcul **doar notele validate**. Înainte de închidere, verifică ce a rămas în ciornă — o notă nevalidată nu intră în verificările de mai sus, deci un eșec real poate trece neobservat până la validare. Balanța, spre deosebire, include toate notele indiferent de statut — de aici pot apărea diferențe de populație între balanță și fișa de cont dacă mai există ciorne.

## Ce se greșește în practică

- Se face reconcilierea TVA fără să se verifice mai întâi dacă toate notele lunii sunt validate — o notă în ciornă poate ascunde exact eroarea căutată.
- Se tratează orice diferență la TVA sub 1 leu ca „nesemnificativă" fără să se verifice dacă există facturi necontabilizate în fereastră — situația e diferită de o coincidență reală.
- Se face reconcilierea o singură dată, la închidere, în loc să se repete pe parcursul lunii — erorile descoperite cu o săptămână mai devreme sunt mai ieftin de corectat.

## Ce face iConta.eu

Verificările de echilibru rulează automat pe notele validate ale lunii curente. Reconcilierea TVA pe conturi (4427/4426, rezultat decont) rulează în ecranul „Control fiscal", cu toleranța de 1 leu și cu semnalul gri explicit atunci când o coincidență ar putea ascunde facturi necontabilizate, nu doar un rezultat corect. Rămâne responsabilitatea contabilului să valideze notele înainte de închidere — aplicația nu forțează validarea, dar arată clar ce a rămas în ciornă.

[iConta.eu](/)
