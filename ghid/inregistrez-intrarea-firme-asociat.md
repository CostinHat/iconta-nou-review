---
title: "Cum înregistrez intrarea unei firme ca asociat"
description: "Pașii legali pentru ca o persoană juridică să devină asociat într-un SRL, prin transmiterea părților sociale și înscrierea la Registrul Comerțului."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum înregistrez intrarea unei firme ca asociat

O firmă (persoană juridică) poate deveni asociat într-un SRL fie prin cesiune de părți sociale de la un asociat existent, fie prin subscrierea de părți sociale noi, la o majorare de capital social. În ambele cazuri, calitatea de asociat nu produce efecte față de terți decât din momentul înscrierii operațiunii în registrul comerțului.

## Temeiul legal

::: ghid-temei
„Art. 202 (1) Părțile sociale pot fi transmise între asociați.
(2) Dacă actul constitutiv nu prevede altfel, transmiterea către persoane din afara societății este permisă numai dacă a fost aprobată de asociați reprezentând cel puțin trei pătrimi din capitalul social.
Art. 203 (1) Transmiterea părților sociale trebuie înscrisă în registrul comerțului și în registrul de asociați al societății.
(2) Transmiterea are efect față de terți numai din momentul înscrierii ei în registrul comerțului."
— Legea 31/1990 privind societățile, art. 202 alin. (1)-(2) și art. 203 alin. (1)-(2) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- Dacă firma nouă cumpără/preia părți sociale de la un asociat existent, e vorba de o **cesiune de părți sociale** — transmiterea către o persoană din afara societății trebuie aprobată de asociați reprezentând cel puțin 3/4 din capitalul social (dacă actul constitutiv nu prevede un alt cvorum).
- Dacă firma nouă intră prin subscrierea de părți sociale suplimentare (majorare de capital social), operațiunea presupune modificarea actului constitutiv, potrivit regulilor de la Titlul IV din Legea 31/1990.
- Indiferent de cale, societatea trebuie să țină un registru al asociaților, în care se înscriu numele/denumirea fiecărui asociat, partea din capitalul social și orice transfer al părților sociale.
- Transmiterea produce efecte între cedent și cesionar de la data actului, dar față de terți (inclusiv organul fiscal) numai din momentul înscrierii la Registrul Comerțului — până atunci, din perspectiva terților, vechea structură de asociați rămâne valabilă.
- Practic, pașii sunt: hotărârea asociaților (act de cesiune sau hotărâre AGA de majorare, după caz) → actul constitutiv actualizat → depunerea dosarului la Oficiul Registrului Comerțului → înscrierea mențiunii.

## Ce se greșește în practică

- Se consideră că firma nouă a devenit asociat din momentul semnării contractului de cesiune, deși legea leagă efectul față de terți strict de înscrierea la Registrul Comerțului.
- Se omite actualizarea actului constitutiv și a registrului de asociați al societății, deși ambele sunt cerute explicit de lege, pe lângă mențiunea de la Registrul Comerțului.
- Se confundă cesiunea de părți sociale (transfer al unor părți deja existente) cu majorarea de capital social prin aport nou (creare de părți sociale noi) — cele două operațiuni au proceduri și implicații fiscale diferite.
- Nu se verifică cvorumul necesar pentru aprobarea transmiterii către o persoană din afara societății (cel puțin 3/4 din capitalul social, dacă actul constitutiv nu prevede altfel).

## Ce face iConta.eu

La data acestui ghid, iConta.eu **nu are o funcție dedicată de înregistrare a intrării unui nou asociat** (persoană fizică sau juridică) în structura societății. Nu am găsit în cod niciun modul pentru cesiune de părți sociale sau pentru actualizarea automată a registrului de asociați. Aplicația poate importa datele asociaților existenți dintr-o sursă externă (modulul `asociati_import_api.py`), dar operațiunea juridică de intrare a unui nou asociat — actul de cesiune, hotărârea AGA, dosarul la Registrul Comerțului — rămâne, în acest moment, în afara aplicației.

[iConta.eu](/)
