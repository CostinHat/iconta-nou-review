---
title: "Casă de marcat nouă: înregistrare și obligații"
description: "Ce trebuie să facă un operator economic după ce instalează o casă de marcat nouă: registrul național ANAF și conectarea la distanță a aparatului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Casă de marcat nouă: înregistrare și obligații

O casă de marcat nou instalată nu devine funcțională din punct de vedere fiscal doar prin punerea ei în funcțiune fizică — aparatul trebuie evidențiat în registrul național ținut de ANAF și conectat la distanță la sistemul informatic de supraveghere, pentru transmiterea automată a datelor fiscale.

## Temeiul legal

::: ghid-temei
„(1) La nivelul Agenției Naționale de Administrare Fiscală se întocmește în formă electronică un registru național de evidență a aparatelor de marcat electronice fiscale instalate în județe și în sectoarele municipiului București, după caz, denumit în continuare Registru.
[...]
(4) În vederea realizării supravegherii și monitorizării aparatelor de marcat electronice fiscale, operatorii economici prevăzuți la art. 1 alin. (1) au obligația de a asigura conectarea la distanță a aparatelor de marcat electronice fiscale, în vederea transmiterii de date fiscale către Agenția Națională de Administrare Fiscală."
— OUG nr. 28/1999 (republicată), art. 3^1 alin. (1), (4) (sursă: anaf_surse/oug_28_1999.html)
:::

Ce presupune practic instalarea unei case de marcat noi:

- Aparatul trebuie evidențiat în Registrul național de evidență a aparatelor de marcat electronice fiscale, ținut electronic de ANAF, pe județe/sectoare ale municipiului București (art. 3^1 alin. (1)) — informațiile și procedura de înregistrare se stabilesc prin ordin al președintelui ANAF (alin. (2)).
- Distribuitorul autorizat sau unitatea acreditată pentru comercializare/service, prin intermediul căreia s-a achiziționat aparatul, are, de regulă, rolul de a asigura demersurile tehnice de fiscalizare și înregistrare inițială.
- Operatorul economic are obligația proprie, separată, de a asigura **conectarea la distanță** a aparatului, astfel încât acesta să transmită automat date fiscale către ANAF, potrivit procedurii aprobate prin ordin al președintelui ANAF (art. 3^1 alin. (5)).
- Supravegherea și monitorizarea ulterioară a aparatului se realizează de ANAF, în baza acestei conectări (art. 3^1 alin. (3)).

## Ce se greșește în practică

- Se presupune că simpla achiziție și punere în funcțiune a aparatului este suficientă, fără verificarea faptului că el a fost efectiv înregistrat în Registrul național ANAF prin distribuitor/unitatea acreditată.
- Se amână conectarea la distanță a aparatului, considerând-o o etapă tehnică opțională sau ulterioară — este o obligație legală distinctă, prevăzută explicit la art. 3^1 alin. (4).
- Se confundă „fiscalizarea" aparatului (proces tehnic realizat de unitatea acreditată de service) cu obligațiile proprii ale operatorului economic privind conectarea și transmiterea de date, care nu se sting automat prin fiscalizare.

## Ce face iConta.eu

La data acestui ghid, iConta.eu nu gestionează înregistrarea unei case de marcat noi în Registrul național ANAF și nu configurează conectarea la distanță a aparatului — acestea sunt pași realizați de operatorul economic împreună cu distribuitorul/unitatea acreditată a AMEF. Aplicația poate importa, ulterior instalării și fiscalizării, Raportul Z generat de aparat (`core/amef_import.py`, conform OPANAF 146/2018), pentru a prelua automat în contabilitate totalurile de vânzări zilnice pe modalități de plată și cote de TVA.

[iConta.eu](/)
