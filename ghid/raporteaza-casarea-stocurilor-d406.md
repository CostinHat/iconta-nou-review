---
title: "Cum se raportează casarea stocurilor în D406?"
description: "Cum se reflectă o casare de stocuri în secțiunea de Stocuri din SAF-T (D406), raportată doar la solicitarea punctuală a ANAF."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează casarea stocurilor în D406?

Casarea unui stoc (scoaterea din gestiune a unor bunuri deteriorate, expirate sau declasate) e, din perspectiva SAF-T, o mișcare de ieșire ca oricare alta — dar întreaga secțiune de Stocuri se raportează doar dacă și când ANAF o solicită punctual, nu automat la fiecare depunere.

## Temeiul legal

::: ghid-temei
„Informațiile privind «stocurile de produse» și «producție în curs» sunt transmise pe baza unei solicitări specifice din partea organelor fiscale centrale. [...] Declarațiile informative D406 pentru «Stocuri» se depun în termenul stabilit de organul fiscal central, care nu poate fi mai mic de 30 de zile calendaristice de la data solicitării."
— OPANAF nr. 1.783/2021, Anexa 5, pct. 9-10 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)

„Pentru toate plusurile, lipsurile și deprecierile constatate la bunuri [...] comisia de inventariere solicită explicații scrise de la persoanele care au răspunderea gestionării bunurilor."
— OMFP nr. 2.861/2009, pct. 39 (sursă: anaf_surse/omfp_2861_2009.txt)
:::

Cum se leagă cele două reguli, pentru o casare de stoc:

- Casarea rezultă, de regulă, dintr-o inventariere care constată bunuri depreciate, fără mișcare sau nevandabile — procesul-verbal al comisiei de inventariere propune scoaterea din uz/casarea, potrivit OMFP 2.861/2009.
- În SAF-T, o casare se reflectă ca o **mișcare de ieșire** din stocul fizic al articolului respectiv (cantitate care scade din soldul de închidere), fără o contrapartidă de vânzare — dar, ca orice informație din secțiunea „Stocuri" a D406, se raportează abia dacă ANAF a trimis o solicitare specifică pentru acea perioadă, nu la fiecare depunere obișnuită.
- Dacă nu există o solicitare ANAF activă pentru secțiunea de Stocuri, casarea nu generează, în sine, o obligație separată de raportare SAF-T — ea rămâne totuși vizibilă în evidența contabilă și în jurnalele de gestiune ale firmei, pregătită pentru momentul în care ar fi cerută.
- Termenul minim de 30 de zile calendaristice de la solicitare se aplică și aici — indiferent de mărimea sau complexitatea operațiunii de casare.

## Ce se greșește în practică

- Se generează o raportare SAF-T de Stocuri imediat după fiecare casare, fără o solicitare ANAF activă — norma leagă explicit raportarea de „stocuri" de o cerere punctuală, nu de fiecare eveniment de gestiune.
- Se omite documentarea casării prin procesul-verbal al comisiei de inventariere, presupunând că simpla înregistrare contabilă a ieșirii de stoc e suficientă — norma contabilă cere explicații scrise și un proces-verbal al comisiei.
- Se confundă „casarea" cu o simplă corecție de stoc din eroare de gestiune — casarea are, potrivit OMFP 2.861/2009, o procedură proprie de constatare și aprobare, diferită de o corecție tehnică.

## Ce face iConta.eu

Modulul de gestiune al iConta.eu tratează o casare de stoc ca o mișcare de ieșire pentru articolul respectiv, reflectată în soldurile calculate de `core/d406_stocuri.py` la generarea secțiunii de Stocuri din SAF-T, atunci când raportarea e cerută de contabil pentru o anumită perioadă. Documentarea casării prin proces-verbal de inventariere și aprobarea administratorului rămân, la data acestui ghid, în afara aplicației, ca proces administrativ separat.

[iConta.eu](/)
