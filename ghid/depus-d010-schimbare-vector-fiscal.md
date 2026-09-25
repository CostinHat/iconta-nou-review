---
title: "Când trebuie depus D010 pentru o schimbare de vector fiscal"
description: "Termenul legal de 15 zile pentru declararea modificărilor la datele de înregistrare fiscală, inclusiv vectorul fiscal, prin declarația de mențiuni."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Când trebuie depus D010 pentru o schimbare de vector fiscal

„Vectorul fiscal" este totalitatea obligațiilor fiscale declarative permanente ale unui contribuabil (dacă e plătitor de TVA, ce tip de decont depune, dacă are angajați etc.). Orice modificare a acestor date — de exemplu, luarea în evidență ca plătitor de TVA, schimbarea perioadei fiscale sau renunțarea la un regim — trebuie adusă la cunoștința organului fiscal printr-o declarație de mențiuni (formularul 010, pentru persoane juridice), într-un termen fix.

## Temeiul legal

::: ghid-temei
„ART. 88 Modificări ulterioare înregistrării fiscale (1) Modificările ulterioare ale datelor din declarația de înregistrare fiscală trebuie aduse la cunoștință organului fiscal central, în termen de 15 zile de la data producerii acestora, prin completarea și depunerea declarației de mențiuni."
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 88 alin. (1) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Termenul curge de la **data producerii** modificării (de exemplu, data de la care firma devine plătitoare de TVA prin depășirea plafonului), nu de la data la care contabilul observă schimbarea.
- „Vectorul fiscal" este el însuși parte din datele declarate prin declarația de înregistrare fiscală inițială — Codul de procedură fiscală prevede expres că aceasta „cuprinde: datele de identificare a contribuabilului/plătitorului, **datele privind vectorul fiscal**, datele privind sediile secundare [...]".
- Dacă modificarea afectează și certificatul de înregistrare fiscală deja emis, acesta trebuie depus odată cu declarația de mențiuni, pentru anulare și eliberarea unui nou certificat (art. 88 alin. (2)).
- Aceleași reguli se aplică și atunci când contribuabilul constată erori (nu doar modificări reale) în declarația de înregistrare fiscală depusă inițial (art. 88 alin. (4)).

## Ce se greșește în practică

- Se depune declarația de mențiuni abia la următoarea declarație periodică (de TVA sau de impozit), nu în cele 15 zile de la producerea evenimentului.
- Se presupune că modificarea vectorului fiscal se „auto-actualizează" din alte declarații depuse (de exemplu, primul decont de TVA), fără o declarație de mențiuni explicită.
- Se omite depunerea certificatului de înregistrare fiscală vechi odată cu declarația de mențiuni, când modificarea afectează date înscrise pe acesta.
- Se confundă termenul de 15 zile pentru modificări ulterioare cu termenul de 30 de zile aplicabil declarației inițiale de înregistrare fiscală sau înființării de sedii secundare — sunt termene diferite, din articole diferite ale Codului de procedură fiscală.

## Ce face iConta.eu

Din verificarea codului, iConta.eu citește și urmărește **vectorul fiscal al firmei** (regim fiscal, calitate de plătitor de TVA, tip de decont, operațiuni intracomunitare) dintr-un profil centralizat al firmei, folosit pentru a determina automat ce declarații sunt datorate și când (`control_fiscal_api.py`). Aplicația nu depune însă, la data acestui ghid, formularul D010 propriu-zis către ANAF — generarea automată a acestei declarații este blocată tehnic, întrucât formularul nu are, la momentul verificării, un validator XML oficial disponibil în canalul ANAF pe care aplicația îl folosește pentru celelalte declarații. Practic, aplicația vă ajută să identificați că vectorul fiscal s-a schimbat, dar depunerea propriu-zisă a D010 rămâne, deocamdată, manuală.

[iConta.eu](/)
