---
title: Gestiune cantitativă sau global-valorică la un restaurant?
description: Un restaurant cu meniu numeros și marje relativ similare pe preparate se poate ține în regim global-valoric, dar evidența cantitativ-valorică pe cost mediu ponderat rămâne alternativa mai simplă dacă nu se dorește gestionarea coeficientului de repartizare și a conturilor 378/4428.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Gestiune cantitativă sau global-valorică la un restaurant?

Un restaurant are, de regulă, exact profilul pentru care legea permite metoda prețului cu amănuntul: meniu numeros, mișcare rapidă a materiilor prime/preparatelor, marje relativ similare pe categorii. Dar nu e singura opțiune posibilă — un restaurant poate ține la fel de legal evidența cantitativ-valorică, pe cost mediu ponderat, dacă preferă să urmărească fiecare produs individual.

## Temeiul legal

::: ghid-temei
> "286. - (1) În funcție de specificul activității, pentru determinarea costului pot fi folosite,
> de asemenea, metoda costului standard, în activitatea de producție sau **metoda prețului cu
> amănuntul, în comerțul cu amănuntul**."
>
> "(8) În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina
> costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru
> care nu este practic să se folosească altă metodă. În această situație, **costul bunurilor
> vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor**.
> Orice modificare a prețului de vânzare presupune recalcularea marjei brute."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 286 alin. (1) și (8).

> "96. - (1) Costul stocurilor din aceeași categorie și al tuturor elementelor fungibile se
> calculează prin aplicarea uneia din următoarele metode: a) metoda costului mediu ponderat - CMP;
> b) metoda primul intrat-primul ieșit - FIFO; c) metoda ultimul intrat-primul ieșit - LIFO. (2)
> Metoda «costului mediu ponderat» (CMP) presupune calcularea costului fiecărui element pe baza
> mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei și a
> costului elementelor similare produse sau cumpărate în timpul perioadei."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 96 alin. (1)-(2).
:::

## Diferența practică pentru un restaurant

La global-valoric, restaurantul nu urmărește costul fiecărui fel de mâncare separat, ci ține mărfurile/materiile la valoare de vânzare cu amănuntul, cu adaosul în 378 și TVA neexigibilă în 4428, descărcate lunar printr-un coeficient de repartizare K. Avantaj: mai puțină administrare pe rețete individuale. Dezavantaj: coeficientul K e o medie — nu spune cât a costat exact un anumit fel de mâncare vândut.

La cantitativ-valoric (CMP), fiecare produs/materie primă are propria fișă de magazie, cu cost mediu ponderat recalculat după fiecare intrare. Avantaj: cost real, urmăribil, per produs — util pentru calcul de rentabilitate pe fel de mâncare. Dezavantaj: cere evidență mai detaliată, mai ales dacă rețetele au multe ingrediente.

## Ce se greșește în practică

- Se alege global-valoric doar pentru „mai puține înregistrări”, fără să se ia în calcul că informația de cost per preparat se pierde.
- Se ține evidență cantitativ-valorică pe materii prime, dar se raportează vânzările ca la global-valoric (cu adaos și 378/4428), amestecând cele două logici.
- Se schimbă metoda în cursul anului fără nicio justificare, ceea ce rupe continuitatea calculelor (coeficientul K cumulat de la 1 ianuarie, la global-valoric, sau costul mediu ponderat recalculat continuu, la CMP).
- Se presupune că restaurantul, servind mâncare la o singură cotă de TVA, nu are niciodată produse la altă cotă — de fapt băuturile alcoolice sau vânzările la pachet pot avea cotă diferită de cea aplicată mesei servite.

## Ce face iConta.eu

Cele două module sunt separate și alese explicit. La global-valoric, `nir_gv` calculează costul, adaosul și TVA la fiecare recepție, iar `descarcare_gv`/`descarca_luna` descarcă lunar costul mărfii vândute (607), adaosul (378) și TVA neexigibilă (4428) folosind coeficientul K calculat din rulaje cumulate de la 1 ianuarie. La cantitativ-valoric (`core/stocuri_cv.py`), fiecare articol are o fișă de magazie proprie, cu costul mediu ponderat recalculat după fiecare intrare (`fisa_magazie`), iar ieșirea se înregistrează direct 607=371 la valoarea CMP × cantitate — fără conturile 378/4428 și fără coeficient de repartizare.

Dacă restaurantul optează pentru global-valoric, trebuie știut că TVA-ul descărcat lunar din 4428 e o aproximare calculată dintr-o cotă medie ponderată a stocului cumulat, nu din mixul real de cote al bonurilor emise în lună — un cost suplimentar de verificare pe care evidența cantitativ-valorică, neavând deloc contul 4428, nu îl are.

[iConta.eu](/)
