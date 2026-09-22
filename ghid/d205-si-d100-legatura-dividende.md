---
title: D205 și D100 - cum se leagă pentru dividende?
description: D100 nu conține nicio linie pentru impozitul pe dividende — impozitul reținut la sursă din dividende se declară exclusiv prin D205, iar cele două declarații nu se reconciliază între ele.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# D205 și D100 - cum se leagă pentru dividende?

Multor contabili li se pare firesc să caute o corespondență între sumele din D100 (declarația unică de obligații de plată) și impozitul pe dividende din D205, așa cum verifică și alte obligații fiscale încrucișat. Pentru dividende însă această legătură nu există, și e important să înțelegeți de ce, ca să nu pierdeți timp căutând o reconciliere care nu are corespondent fiscal.

## Temeiul legal

::: ghid-temei
„Obligaţia calculării şi reţinerii impozitului pe veniturile sub formă de dividende revine persoanelor juridice, odată cu plata dividendelor.../sumelor... de către acţionari/asociaţi/investitori. Termenul de virare a impozitului este până la data de 25 inclusiv a lunii următoare celei în care se face plata." (Legea 141/2025, art.II pct.5, care modifică art.97 alin.(7) CF)

„Declaraţia se completează şi se depune de către plătitorii de venituri care au obligaţia calculării, reţinerii şi virării impozitului pe veniturile cu regim de reţinere la sursă a impozitului... pentru următoarele tipuri de venituri: a) venituri din dividende; b) venituri din dobânzi; c) venituri din lichidarea unei persoane juridice; d) venituri din pensii; e) venituri din premii; f) venituri din jocuri de noroc; g) venituri din alte surse...; h) venituri din activităţi independente..." (OPANAF 179/2022, I.1)
:::

## De ce nu există o reconciliere D205 ↔ D100

D100 este declarația prin care se raportează obligațiile de plată curente ale firmei — printre altele, impozitul pe veniturile microîntreprinderilor și impozitul pe profit trimestrial. Impozitul reținut la sursă din dividende plătite persoanelor fizice **nu se regăsește ca obligație distinctă în D100** — D100 nu are un cod de obligație dedicat impozitului pe dividende. Acest impozit se declară și se plătește separat, exclusiv prin D205, conform termenului din Legea 141/2025 (25 ale lunii următoare plății, respectiv 25 ianuarie pentru dividendele distribuite dar neplătite).

Cu alte cuvinte, cele două declarații răspund la întrebări diferite: D100 spune „cât datorează firma la impozit pe profit/pe venitul microîntreprinderii", iar D205 spune „cât impozit a reținut firma de la fiecare beneficiar de dividende". Nu există, la nivel de conținut declarat, o sumă comună de verificat între ele.

## Ce se greșește în practică

- Se caută în D100 o linie pentru „impozit dividende" care pur și simplu nu există în structura declarației.
- Se amână depunerea D205 în așteptarea unei „confirmări" din D100 care nu va apărea niciodată.
- Se presupune că o eventuală diferență între D205 și D100 semnalează o eroare, deși cele două nu au niciun câmp comparabil pentru dividende.
- Se ignoră faptul că verificarea reală de conținut a D205 se face altfel (vezi ghidul „Cum verific impozitul pe dividende din D205 cu D100?"), nu prin comparație cu D100.

## Ce face iConta.eu

Generatorul D205 recalculează independent, printr-o a doua cale de verificare separată de motorul principal, baza și impozitul per beneficiar din mișcările contului 457, și blochează generarea declarației dacă cele două calcule diverg. Această a doua cale nu compară însă D205 cu D100 — pentru că D100 în acest cod generează doar obligațiile de impozit micro/profit și nu conține deloc impozitul pe dividende, o comparație D205↔D100 ar citi practic aceeași informație (contul 457) de două ori, fără să valideze nimic real. Verificarea de conținut a D205 se face deci intern, din contabilitate, nu prin comparație cu D100.

[iConta.eu](/)
