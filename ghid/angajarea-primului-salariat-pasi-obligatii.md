---
title: "Angajarea primului salariat: pași și obligații 2026"
description: "Ce date reale cere un prim angajat în evidența unei firme și unde apare, în lege, singura verificare de fond pe care aplicația nu o face automat."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Angajarea primului salariat: pași și obligații 2026

Când o firmă angajează primul salariat, contabilul trebuie să strângă și să introducă un set minim de date corecte — CNP, dată de angajare, tip de normă, ocupație (COR), salariu brut — pentru ca statul de plată, declarația 112 și înregistrarea în REGES-ONLINE să pornească fără erori. Una dintre aceste date, tipul de normă, are un prag legal precis pe care merită să-l cunoști înainte de completare, pentru că nu toate aplicațiile îl verifică pentru tine.

## Temeiul legal

::: ghid-temei
„Angajatorul poate încadra salariaţi cu program de lucru corespunzător unei fracţiuni de norma de cel puţin două ore pe zi, prin contracte individuale de muncă pe durata nedeterminată sau pe durata determinata, denumite contracte individuale de muncă cu timp parţial. [...] Durata saptamanala de lucru a unui salariat angajat cu contract individual de muncă cu timp parţial este inferioară celei a unui salariat cu norma întreaga comparabil, fără a putea fi mai mica de 10 ore."
— Legea 53/2003 (Codul Muncii), art. 101 alin. (1) și (3) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

- Norma parțială e permisă doar dacă programul e de **cel puțin 2 ore pe zi**.
- La nivel săptămânal, timpul de lucru al unui salariat cu normă parțială nu poate fi **mai mic de 10 ore**.
- Sub aceste praguri, angajarea nu se mai încadrează legal în forma „timp parțial" reglementată de art. 101.
- Distincția legală e doar între normă întreagă și normă parțială — legea nu impune un câmp separat de „tip de contract" pentru acest aspect, ci reglementează efectiv doar durata timpului de lucru.

## Ce se greșește în practică

- Se introduce o normă parțială cu doar 1 oră/zi sau 5 ore/săptămână, fără să se verifice pragul legal de la art. 101 — pentru că nimeni, nici contabilul, nici softul, nu compară valoarea introdusă cu minimul din lege.
- Se lasă câmpul de cod ocupație (COR) necompletat sau se scrie un cod inventat, deși existența lui reală în nomenclator e obligatorie pentru declarația 112 și pentru REGES.
- Se confundă salariul brut din contract cu salariul care ajunge efectiv în calculul fiscal, deși cele două trebuie introduse identic pentru ca statul de plată să reflecte realitatea.
- Se presupune că un CNP „cu format corect" (13 cifre) e suficient, ignorând cifra de control, care poate respinge tacit declarația 112 mai târziu.

## Ce face iConta.eu

La crearea unui salariat, din formularul „Salariat nou" (parte din ecranul **Stat de plată**, nu un card separat „Salariați"), iConta.eu cere obligatoriu nume, CNP, dată de angajare, cod COR (verificat direct în nomenclator, nu ca text liber) și salariu brut mai mare decât zero. CNP-ul, dacă e completat, e validat cu algoritmul complet cu cifră de control (mod-11), nu doar ca format de 13 cifre — exact pentru a preveni o declarație 112 respinsă tăcut. Tipul de normă (întreagă/parțială) e validat doar ca literal admis, nu ca prag legal: **iConta.eu nu verifică** dacă orele introduse la normă parțială respectă minimul de 2 ore/zi și 10 ore/săptămână de la art. 101 — rămâne responsabilitatea contabilului să respecte acest prag la completare. Odată creat, salariatul alimentează automat statul de plată și declarația 112; identitatea (CNP, nume, prenume) e pregătită pentru REGES-ONLINE, dar transmiterea propriu-zisă se face separat, manual, cu butonul „Trimite în REGES", nu automat la crearea salariatului.

[iConta.eu](/)
