---
title: "Ce fac dacă balanța nu este echilibrată?"
description: O balanță neechilibrată are, de regulă, una din două cauze concrete — o notă contabilă cu o parte lipsă sau solduri inițiale care nu se potrivesc — și ambele se pot localiza sistematic.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Ce fac dacă balanța nu este echilibrată?

Balanța de verificare există exact pentru asta: să arate dacă suma tuturor debitelor este egală cu suma tuturor creditelor din contabilitate. Când nu este, nu înseamnă că trebuie refăcută toată luna — înseamnă că undeva, cel mai probabil, există o singură notă contabilă cu o parte lipsă sau un sold inițial introdus greșit.

## Temeiul legal

::: ghid-temei
„Pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate, lunar se întocmește balanța de verificare."
— Legea contabilității (Legea 82/1991), art. 22
:::

Balanța de verificare este, prin construcție legală, instrumentul de control al corectitudinii înregistrărilor — nu un raport opțional. Dacă ea nu este echilibrată, principiul dublei înregistrări (fiecare operațiune afectează simetric un cont debitor și un cont creditor, cu aceeași sumă) a fost încălcat undeva în date, iar sarcina practică este să găsiți exact unde.

Există, în esență, două surse posibile de dezechilibru, cu semnale diferite:
1. **O notă contabilă cu suma introdusă doar pe debit sau doar pe credit** (cont lipsă, gol sau format greșit) — aici dezechilibrul apare direct în rulajele perioadei curente.
2. **Soldurile inițiale ale conturilor nu se închid** — suma soldurilor debitoare nu este egală cu suma soldurilor creditoare la începutul perioadei, de obicei pentru că o balanță anterioară a fost introdusă manual, incomplet, sau pentru că lipsește un sold de deschidere pe un cont care ar trebui să îl aibă.

Localizarea corectă a cauzei economisește timp: verificați întâi dacă dezechilibrul apare deja în rulajele lunii curente (cauza 1) sau doar în soldurile reportate de la începutul perioadei (cauza 2) — cele două nu se rezolvă la fel.

## Ce se greșește în practică

Cea mai costisitoare greșeală este să se „forțeze" echilibrul prin adăugarea unei note artificiale, cu un cont oarecare, doar ca balanța să iasă la zero — asta ascunde eroarea reală în loc să o rezolve și complică orice control ulterior. O altă greșeală frecventă este să se caute eroarea manual, notă cu notă, pe o lună întreagă, în loc să se folosească un instrument de verificare care izolează exact liniile cu o parte de cont lipsă sau soldurile care nu se potrivesc.

## Ce face iConta.eu

Aplicația rulează, la fiecare verificare a perioadei, două controale distincte de echilibru: unul pe liniile brute ale perioadei curente (prinde nota cu o parte de cont lipsă) și unul pe soldurile inițiale reportate (prinde soldurile care nu se închid între ele). Cele două verificări sunt afișate compus, pe ecranul de control fiscal, ca un singur indicator „Echilibru" — dar mecanismele din spate sunt separate tocmai pentru că sursele de dezechilibru sunt diferite, iar una nu o prinde pe cealaltă.

[iConta.eu](/)
