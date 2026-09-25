---
title: "Cum verific ultima declarație fiscală valabilă pentru o perioadă?"
description: "Orice declarație — de impunere sau informativă — poate fi corectată prin declarații rectificative succesive; ce înseamnă asta pentru «versiunea valabilă» și cum ține evidența iConta.eu, intern, între depuneri."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum verific ultima declarație fiscală valabilă pentru o perioadă?

Pentru orice tip de declarație — D100, D112, D300, D390, D394, D406 — legea permite corectarea prin depunerea unei declarații rectificative, iar aceasta din urmă devine noua versiune valabilă pentru acea perioadă. „Ultima declarație valabilă" nu e deci întotdeauna prima depusă, ci ultima rectificativă acceptată — un lucru simplu de spus, dar care poate produce erori reale dacă sistemul care ține evidența nu distinge clar între depuneri succesive pentru aceeași perioadă.

## Temeiul legal

::: ghid-temei
„(1) Declarația de impunere poate fi corectată de către contribuabil/plătitor, pe perioada termenului de prescripție a dreptului de a stabili creanțe fiscale.
(2) Declarația informativă poate fi corectată de către contribuabil/plătitor indiferent de perioada la care se referă.
(3) Declarațiile prevăzute la alin. (1) și (2) pot fi corectate prin depunerea unei declarații rectificative."
— Legea 207/2015 (Codul de procedură fiscală), art. 105 alin. (1)-(3) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Regula acoperă **ambele** categorii de declarații: cele de impunere (unde contribuabilul calculează el obligația — D100, D112, D300) și cele informative (D406/SAF-T) — dar cu limite de timp diferite: cele de impunere doar în termenul de prescripție, cele informative oricând.
- Mecanismul tehnic e mereu același: **o nouă depunere**, nu o modificare a celei vechi — legea vorbește de „depunerea unei declarații rectificative", deci fiecare corecție e un act nou, distinct de cel inlocuit.
- Legea nu spune nimic despre CUM trebuie păstrată, intern, la contribuabil sau la furnizorul lui de software, istoria acestor depuneri succesive — asta ține strict de arhitectura sistemului folosit, nu de normă.

## Ce se greșește în practică

- Se presupune că orice sistem care ține „ultima declarație depusă" arată automat corect ultima variantă — dacă sistemul suprascrie pur și simplu vechea depunere cu una nouă pentru aceeași perioadă, fără versionare explicită, o coliziune tehnică (ex. o rectificativă depusă la câteva minute distanță) poate face să rămână salvată din greșeală prima variantă, nu a doua.
- Se confundă „am regăsit o declarație pentru luna X" cu „aceea e cea corectă" — fără un criteriu explicit de ordonare (număr de depunere, dată), nu poți ști dacă e vorba de inițială sau de o rectificativă ulterioară.
- Se folosește data fișierului local (XML salvat pe calculator) ca reper pentru „ultima variantă", deși fișierele locale nu reflectă neapărat ordinea reală a depunerilor la organul fiscal.

## Ce face iConta.eu

Intern, iConta.eu păstrează, pentru fiecare depunere reușită, XML-ul trimis și rândurile calculate, într-un tabel versionat: cheia de identificare a unei depuneri include explicit un număr de depunere care crește la fiecare redepunere pentru același tenant/an/lună/tip de declarație, iar o vedere dedicată din baza de date selectează mereu depunerea cu numărul cel mai mare — adică ultima. Acest lucru nu a fost dintotdeauna așa: varianta inițială (implementată și respinsă în aceeași zi, 22.07.2026) ignora tăcut o a doua depunere pentru aceeași perioadă (first-write-wins), ceea ce ar fi însemnat exact greșeala descrisă mai sus — controlul intern ar fi comparat mereu cu actul înlocuit, nu cu cel în vigoare. Decizia a fost inversată în aceeași zi, tocmai pentru acest motiv.

Ce nu face acest mecanism: nu expune direct utilizatorului XML-ul sau rândurile calculate ale declarațiilor — niciunul din punctele din aplicație care citesc această evidență (destinate portalului clienților sau rapoartelor de documente) nu arată decât tipul, anul, luna și data ultimei depuneri pentru fiecare declarație. Verificarea conținutului detaliat al ultimei versiuni rămâne, la acest moment, o operațiune internă de sistem, nu un ecran dedicat vizibil contabilului.

[iConta.eu](/)
