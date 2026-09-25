---
title: "Înregistrarea firmei nou înființate la ANAF"
description: "Firma nou înființată trebuie să depună declarația de înregistrare fiscală în 30 de zile de la înființare, pentru a primi vectorul fiscal și certificatul de înregistrare."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Înregistrarea firmei nou înființate la ANAF

Înființarea unei firme la Registrul Comerțului nu încheie singură procesul de „pornire" din perspectivă fiscală — urmează pasul separat al înregistrării fiscale, prin care ANAF stabilește ce declarații va datora firma și îi atribuie, dacă e cazul, codul de identificare fiscală. Termenul pentru acest pas e strict și adesea trecut cu vederea.

## Temeiul legal

::: ghid-temei
„(6) Declarația de înregistrare fiscală se depune în termen de 30 de zile de la: a) data înființării potrivit legii, în cazul persoanelor juridice, asocierilor și al altor entități fără personalitate juridică; [...]"
— Legea nr. 207/2015 privind Codul de procedură fiscală, art. 82 alin. (6) lit. a) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Declarația de înregistrare fiscală cuprinde datele de identificare ale firmei, dar și **datele privind vectorul fiscal** — adică tipurile de obligații fiscale pentru care firma va avea de acum înainte obligații de declarare (impozit pe profit/micro, TVA, contribuții salariale etc.).
- Pe baza declarației, organul fiscal eliberează certificatul de înregistrare fiscală, în termen de 10 zile de la depunere, document care cuprinde obligatoriu codul de identificare fiscală.
- Orice modificare ulterioară a datelor din declarația inițială (de exemplu devenirea plătitoare de TVA) trebuie adusă la cunoștința organului fiscal în 15 zile de la producerea ei, prin declarație de mențiuni.

## Ce se greșește în practică

- Se presupune că înregistrarea la Registrul Comerțului e suficientă și că vectorul fiscal se stabilește automat, fără o declarație separată depusă la organul fiscal.
- Termenul de 30 de zile e depășit din lipsă de atenție, mai ales la firmele înființate de asociați fără contabil angajat încă din prima zi.
- Modificările ulterioare ale vectorului fiscal (de exemplu opțiunea pentru plătitor de TVA) sunt aplicate „de fapt" în activitate, fără să fie comunicate organului fiscal în termenul legal de 15 zile.

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu are un modul (`vector_fiscal_api`) care citește și gestionează vectorul fiscal al firmei deja configurate în aplicație (regim fiscal, calitate de plătitor de TVA, periodicitatea decontului, operațiuni intracomunitare) și îl folosește pentru a determina ce declarații sunt datorate. Aplicația **nu** depune însă efectiv declarația de înregistrare fiscală la ANAF — acel pas administrativ inițial rămâne în afara aplicației; iConta.eu preia vectorul fiscal ca informație deja existentă, pentru a organiza declarațiile ulterioare.

[iConta.eu](/)
