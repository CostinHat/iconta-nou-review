---
title: 'Descărcarea de gestiune 2026: cum se face corect lunar'
description: Descărcarea lunară calculează coeficientul de adaos cumulat de la 1 ianuarie, îl aplică doar vânzărilor lunii curente și generează o notă de descărcare la ultima zi calendaristică a lunii, propusă ca ciornă pentru validare de către contabil.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Descărcarea de gestiune 2026: cum se face corect lunar

Descărcarea de gestiune la o firmă cu evidență global-valorică (preț cu amănuntul) nu e o simplă „scoatere din stoc” a mărfii vândute — presupune un calcul specific, cumulat pe exercițiul financiar, care separă costul de achiziție de adaosul comercial și de TVA-ul neexigibil aferent vânzărilor lunii.

## Temeiul legal

::: ghid-temei
„Repartizarea diferențelor de preț asupra valorii bunurilor ieșite și asupra stocurilor se efectuează cu ajutorul unui coeficient care se calculează astfel: Coeficient de repartizare = [Soldul inițial al diferențelor de preț + Diferențe de preț aferente intrărilor în cursul perioadei, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] / [Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț de înregistrare, cumulat de la începutul exercițiului financiar până la finele perioadei de referință] x 100.”

„(7) Diferențele de preț se repartizează proporțional atât asupra valorii bunurilor ieșite, cât și asupra bunurilor rămase în stoc.”

— *OMFP 1802/2014, pct. 286 alin. (4) și (7).*
:::

## Pașii descărcării lunare, corect

1. **Calculați coeficientul K** cumulat de la 1 ianuarie până la sfârșitul lunii curente, folosind soldurile inițiale (dacă există) și rulajele validate ale conturilor 371, 378 și 4428.
2. **Aplicați K doar la vânzările lunii curente** (rulajul contului 707 aferent lunii respective, nu cumulat pe an) — separarea cost/adaos/TVA se face lunar, chiar dacă baza de calcul K e cumulată.
3. **Generați nota de descărcare** cu suma rezultată — cost vândut (607), adaos aferent (378) și TVA neexigibilă aferentă (4428) — datată la ultima zi calendaristică a lunii.
4. **Validați manual nota**, verificând-o înainte de închiderea lunii — nota de descărcare e propusă automat ca ciornă, nu se validează de la sine.
5. **Dacă nu au existat vânzări în lună**, nu se generează nicio notă de descărcare „pe zero” — nu forțați o notă artificială doar ca să „completați” fiecare lună.

## Ce se greșește în practică

- Se calculează coeficientul K doar din datele lunii curente, nu cumulat pe exercițiu — regula legală cere explicit calcul cumulat de la 1 ianuarie.
- Se validează automat, fără verificare, nota de descărcare propusă — descărcarea e un calcul mecanic corect doar dacă datele de intrare (rulajele validate din lunile anterioare) sunt, la rândul lor, corecte.
- Se corectează o eroare descoperită într-o lună anterioară doar prin modificarea directă a notei deja validate — odată validată, o notă nu mai poate fi editată sau ștearsă; corecția se face printr-o notă manuală de stornare/ajustare, nu prin „repararea” celei vechi.
- Se amestecă, pe rulajul contului 4428, mișcările din descărcarea de gestiune cu cele dintr-un mecanism separat (de exemplu, TVA la încasare), denaturând coeficientul K.

## Ce face iConta.eu

`core/stocuri_api.py`, funcția `descarca_luna(conn, schema, an, luna)`, implementează exact acest flux: calculează cumulat de la 1 ianuarie (`inceput_an`), citește soldurile inițiale din tabela `solduri_initiale` (dacă există) și rulajele 371/378/4428 din notele **validate** (`status='validata'`), filtrează vânzările (707) doar pe luna curentă și doar din sursele de gestiune relevante (`horeca_z`, `stocuri`, `facturi_marfa`). Nota de descărcare se creează la ultima zi calendaristică a lunii, ca **ciornă** — contabilul o validează manual în jurnal, conform textului de ajutor al funcționalității: „AI propune (note ciorne), contabilul validează”. Dacă nu sunt vânzări în lună, nu se generează nicio notă.

**Limitare confirmată**: nu există, în `core/jurnal_api.py`, nicio funcție de corecție/stornare dedicată pentru o descărcare deja validată greșit — notele validate nu pot fi editate sau șterse; corectarea se face printr-o notă manuală de ajustare, scrisă de contabil. De asemenea, rulajele 371/378/4428 din `descarca_luna` nu sunt filtrate pe sursă (spre deosebire de 707) — dacă firma combină gestiunea global-valorică cu note manuale pe 4428 din alt mecanism, verificați separat sursa acestora înainte de a valida.

[iConta.eu](/)
