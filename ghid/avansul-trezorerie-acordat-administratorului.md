---
title: "Avansul de trezorerie acordat administratorului"
description: "Plafonul zilnic de 5.000 lei pentru plățile din avansuri spre decontare acordate unei persoane, conform Legii 70/2015, și documentul obligatoriu de acordare."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Avansul de trezorerie acordat administratorului

Un avans de trezorerie dat administratorului (pentru deplasări, achiziții mărunte, cheltuieli curente) nu e o operațiune fără limite — legea privind restrângerea plăților în numerar impune un plafon zilnic explicit, calculat separat pentru fiecare persoană care primește astfel de avansuri.

## Temeiul legal

::: ghid-temei
„Articolul 3
(1) Prin excepție de la prevederile art. 1 alin. (1) se pot efectua operațiuni de încasări și plăți în numerar, în următoarele condiții: [...]
e) plăți din avansuri spre decontare, în limita unui plafon zilnic de 5.000 lei, stabilit pentru fiecare persoană care a primit avansuri spre decontare.
[...]
(4) La data acordării avansurilor spre decontare, sumele aferente intră în calculul plafonului zilnic prevăzut la alin. (1) lit. c) sau d), după caz."
— Legea 70/2015 (pentru întărirea disciplinei financiare privind operațiunile de încasări și plăți în numerar), art. 3 alin. (1) lit. e), alin. (4) (sursă: anaf_surse/legea_70_2015_consolidat.txt)

„(1) Nerespectarea prevederilor art. 1 alin. (1), art. 3 alin. (2) și (3), art. 4 alin. (1), (2) și (4), art. 9 și 10 constituie contravenții [...] și se sancționează [...] cu amendă de 10% din suma încasată/plătită care depășește plafonul stabilit de prezentul capitol pentru fiecare tip de operațiune, dar nu mai puțin de 100 lei."
— Legea 70/2015, art. 12 alin. (1) (sursă: anaf_surse/legea_70_2015_consolidat.txt)
:::

Ce rezultă concret pentru avansul dat administratorului:

- **Plafonul e de 5.000 lei pe zi, per persoană** — nu per operațiune și nu la nivelul întregii firme; dacă administratorul primește mai multe avansuri în aceeași zi, suma lor cumulată nu poate depăși 5.000 lei.
- **Momentul acordării avansului contează pentru plafon** — alin. (4) leagă explicit acordarea avansului de calculul plafonului zilnic de plăți, deci suma dată ca avans „consumă" din plafonul zilnic de plăți în numerar al firmei, nu doar din plafonul separat al avansurilor.
- **Atenție la temeiul exact al sancțiunii:** art. 12 alin. (1) leagă amenda de 10% (minim 100 lei) de nerespectarea art. 1 alin. (1), art. 3 alin. (2) și (3) (interdicția fragmentării încasărilor/plăților), art. 4 alin. (1), (2) și (4), art. 9 și 10 — **nu menționează explicit art. 3 alin. (1)**, articolul care stabilește chiar plafonul avansurilor spre decontare (lit. e). Depășirea propriu-zisă a plafonului de 5.000 lei/zi la un avans nu are, în textul de la art. 12 alin. (1), o mențiune la fel de directă ca fragmentarea plăților către furnizori; prudența practică rămâne totuși să nu se depășească plafonul, indiferent de nuanța strict textuală a articolului sancționator.
- Documentarea acordării avansului se face prin **Dispoziția de plată către casierie** (cod 14-4-4, conform OMFP 2634/2015) — documentul justificativ standard pentru plata în numerar a avansurilor pentru cheltuieli, inclusiv cele acordate administratorului.

## Ce se greșește în practică

- Se acordă administratorului un avans unic de peste 5.000 lei, presupunând că plafonul se aplică doar operațiunilor „obișnuite" de plată, nu și avansurilor — legea include explicit avansurile spre decontare în categoria supusă plafonului.
- Se acordă mai multe avansuri mici, în aceeași zi, către aceeași persoană, fără să se verifice suma lor cumulată — plafonul se calculează pe total zilnic per persoană, nu pe fiecare tranșă separat.
- Se ignoră faptul că administratorul, ca orice altă persoană care primește avansuri spre decontare, e supus aceluiași plafon — nu există o excepție legală pentru calitatea de administrator.

## Ce face iConta.eu

Modulul de casierie din iConta.eu (`core/casa.py`) verifică automat plafonul zilnic al avansurilor spre decontare (funcția `verifica_plafon`), cu temeiul legal atașat direct în cod (Legea 70/2015, plafon de 5.000 lei/persoană/zi), și semnalează depășirile ca avertisment de risc la control. Aplicația generează și notele contabile de acordare (`avans_acordare`), restituire (`avans_restituire`) și decontare (`avans_deconteaza`) a avansurilor de trezorerie (contul 542), cu sold urmărit pe fiecare titular de avans.

[iConta.eu](/)
