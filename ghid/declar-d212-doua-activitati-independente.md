---
title: "Cum declar în D212 dacă am două activități independente?"
description: Veniturile din mai multe activități independente se cumulează într-o singură bază de calcul CAS și într-o singură bază de calcul CASS — nu se calculează separat, pe fiecare activitate.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum declar în D212 dacă am două activități independente?

Legea nu tratează două activități independente (de exemplu, două PFA-uri, sau un PFA și o asociere fără personalitate juridică) ca fiind independente una de alta pentru CAS și CASS — veniturile lor nete se adună într-o singură bază de calcul, comună.

## Temeiul legal

::: ghid-temei
**Art. 148 alin. (1) Cod fiscal (Legea 227/2015):** *„Persoanele fizice care ... au realizat venituri din activitățile prevăzute la art. 137 alin. (1) lit. b) și b^1), din una sau mai multe surse ..., a căror valoare anuală cumulată este cel puțin egală cu 12 salarii minime brute pe țară, datorează contribuția de asigurări sociale ..."*

**Art. 170 alin. (1) Cod fiscal**, modificat de Legea 239/2025 art. XII pct. 19: *„Persoanele fizice care ... au realizat venituri din cele prevăzute la art. 155 alin. (1) lit. b), din una sau mai multe surse, datorează contribuția de asigurări sociale de sănătate la o bază anuală de calcul egală cu suma rezultată prin cumularea venitului net anual realizat ..."*
:::

## Ce înseamnă „din una sau mai multe surse"

Formularea de mai sus, identică la CAS și la CASS, e cea care rezolvă întrebarea: dacă ai două activități independente, veniturile nete din amândouă se **adună**, iar plafoanele (12/24 salarii minime pentru CAS, pragul de 6 salarii minime și plafonul de 60/72 salarii minime pentru CASS) se aplică asupra sumei cumulate, nu separat, pe fiecare sursă.

Practic:

- Faci suma veniturilor nete din toate activitățile independente ale anului.
- Verifici încadrarea sumei totale în treptele CAS (sub/între/peste 12 și 24 sm).
- Verifici încadrarea aceleiași sume totale în plafonul CASS (sub/între/peste 6 sm și plafonul maxim).
- Impozitul (10%) se calculează, la rândul lui, pe venitul net cumulat, minus CAS și CASS rezultate din calculul comun.

## Ce se greșește în practică

- **Se calculează CAS și CASS separat pe fiecare activitate**, ca și cum ar fi doi contribuabili diferiți — greșit; plafoanele se aplică o singură dată, pe suma veniturilor din toate sursele.
- **Se declară două fișe fiscale separate în D212**, fără să se cumuleze veniturile nete înainte de a verifica plafoanele — riscul e fie plata dublă a CAS-ului minim (dacă fiecare activitate „intră" separat pe treapta de 12 sm), fie omiterea CASS-ului dacă niciuna dintre activități, luată separat, nu atinge pragul de 6 sm, deși suma lor îl atinge.

## Ce face iConta.eu

Fișa D212 (RIP > Fișa D212) din aplicație calculează cifrele pe baza registrului de încasări și plăți al unei singure activități/tenant. Dacă ai două activități independente înregistrate separat în aplicație (doi „tenanți" distincți), aplicația **nu cumulează automat** veniturile nete ale celor două fișe într-o singură bază CAS/CASS — cumularea cerută de art. 148 alin. (1) și art. 170 alin. (1) rămâne, în acest caz, un pas manual: se calculează separat fiecare fișă, apoi contabilul adună venitul net al ambelor și recalculează CAS/CASS pe suma totală, înainte de completarea Declarației unice. Pașii concreți de completare în ecranul curent de D212 nu fac parte din acest ghid — aplicația a primit modificări recente la acest ecran, care nu au fost încă verificate separat.

[iConta.eu](/)
