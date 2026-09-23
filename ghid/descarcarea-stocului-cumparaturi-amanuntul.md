---
title: "Descărcarea stocului pentru cumpărături cu amănuntul"
description: "Cum se descarcă din gestiune marfa vândută cu amănuntul, la comercianții care țin evidența la preț de vânzare (metoda global-valorică)."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Descărcarea stocului pentru cumpărături cu amănuntul

Când marfa este vândută cu amănuntul și evidența stocurilor se ține la preț de vânzare (metoda global-valorică), descărcarea din gestiune nu se face „pe bucată", ci printr-o notă contabilă unică pe perioadă, calculată cu ajutorul unui coeficient de repartizare.

## Temeiul legal

::: ghid-temei
OMFP 1802/2014, Anexa 1 — Reglementări contabile, pct. 286 alin. (4): „Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100."

pct. 291 alin. (5): „Inventarul intermitent nu se utilizează în comerțul cu amănuntul în situația în care se aplică metoda global-valorică."

(Text consolidat OMFP 1802/2014, verificat pe mirrorul local la 17.09.2026.)
:::

Contul 371 „Mărfuri" trebuie ținut permanent (nu prin inventar intermitent, interzis explicit la alin. 5 de mai sus), iar diferența dintre prețul de vânzare și costul de achiziție se separă pe conturile 378 „Diferențe de preț la mărfuri" (adaos comercial) și 4428 „TVA neexigibilă", folosind coeficientul de repartizare calculat cumulat de la începutul exercițiului financiar.

## Ce se greșește în practică

- Se încearcă descărcarea gestiunii vânzare cu vânzare, ceea ce contrazice logica „cumulat de la începutul exercițiului" a coeficientului de repartizare.
- Se omite validarea manuală a notei contabile — descărcarea calculată automat rămâne o propunere, nu o înregistrare definitivă.
- Se amestecă, pe contul 4428, mișcări provenite din alte mecanisme fiscale (de exemplu regimul de TVA la încasare), ceea ce poate denatura coeficientul — vezi mai jos.

## Ce face iConta.eu

Funcția `descarca_luna` din `core/stocuri_api.py` calculează descărcarea de gestiune cumulat de la 1 ianuarie: preia soldurile inițiale ale conturilor 371/378/4428 (din `solduri_initiale`, dacă există) și rulajele lor din notele **deja validate** de contabil, până la sfârșitul lunii pentru care se face descărcarea. Vânzările (contul 707) sunt filtrate explicit pe sursele `horeca_z`, `stocuri` și `facturi_marfa`, luate doar pe luna curentă (nu cumulat). Nota rezultată este propusă automat ca **ciornă**, la data ultimei zile calendaristice a lunii, iar validarea ei rămâne manuală, în sarcina contabilului.

O atenționare tehnică din cercetarea care stă la baza acestui ghid: spre deosebire de rulajul contului 707 (filtrat explicit pe sursă), rulajele conturilor 371, 378 și 4428 sunt citite **fără filtrare pe sursă**. Contul 4428 este folosit în aplicație și de un ecran separat, manual, de TVA la încasare (art. 282 Cod fiscal). Dacă o firmă folosește ambele mecanisme, notele manuale de TVA la încasare pot influența rulajul 4428 folosit la calculul coeficientului de repartizare. Nu este o eroare confirmată în producție, dar este o lacună de izolare vizibilă în cod, de urmărit de către contabil.

[iConta.eu](/)
