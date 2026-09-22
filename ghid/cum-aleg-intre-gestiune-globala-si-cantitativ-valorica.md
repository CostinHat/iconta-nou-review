---
title: Cum aleg între gestiune globală și cantitativ-valorică?
description: Metoda global-valorică (prețul cu amănuntul) și evidența cantitativ-valorică cu cost mediu ponderat sunt ambele permise de lege, dar alegerea depinde de specificul activității — numărul de articole, mișcarea lor și cât de similare sunt marjele.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum aleg între gestiune globală și cantitativ-valorică?

Legea permite ambele metode, dar pentru scopuri diferite. Metoda global-valorică (prețul cu amănuntul) e gândită pentru comerțul cu amănuntul cu multe articole, mișcare rapidă și marje similare, unde nu e practic să se urmărească fiecare produs individual. Evidența cantitativ-valorică, cu evaluare la cost mediu ponderat (CMP), FIFO sau LIFO, urmărește fiecare articol separat, cu fișă de magazie proprie.

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
> costului elementelor similare produse sau cumpărate în timpul perioadei. [...] (3) Potrivit
> metodei «primul intrat-primul ieșit» (FIFO), bunurile ieșite din gestiune se evaluează la costul
> de achiziție sau de producție al primei intrări (lot). [...]"
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 96 alin. (1)-(3).
:::

## Criteriile care decid alegerea

Pct. 286 alin. (8) leagă explicit metoda global-valorică de trei condiții cumulate: articole numeroase, mișcare rapidă, marje similare. Dacă produsele au marje foarte diferite între ele, sau dacă numărul de articole e mic și fiecare are un cost distinct urmăribil (ex. depozit cu produse de valoare mare, comerț cu ridicata pe contract), evidența cantitativ-valorică (pct. 96) e alegerea firească, pentru că oferă costul real al fiecărui articol, nu o medie la nivel de gestiune.

Legea folosește termenii „pot fi folosite” și „poate fi utilizată” — metoda global-valorică e o opțiune, nu o obligație pentru orice comerț cu amănuntul. Odată aleasă, metoda trebuie aplicată consecvent, iar orice schimbare ulterioară de metodă trebuie justificată în notele explicative ale situațiilor financiare.

## Ce se greșește în practică

- Se alege metoda global-valorică doar pentru că „e mai simplă”, fără să existe de fapt un sortiment numeros cu marje similare — apoi contabilul descoperă că nu poate urmări costul real al unui produs individual când e nevoie (ex. la un litigiu sau la o promoție punctuală).
- Se schimbă metoda de la un exercițiu la altul fără nicio justificare consemnată, deși legea cere consecvență și motivare la schimbare.
- Se crede că metoda global-valorică „scutește” de inventariere anuală sau de urmărire pe stoc — de fapt cere evidență permanentă (inventar permanent, nu intermitent).
- Se ignoră faptul că metoda global-valorică introduce mecanisme suplimentare (coeficient de repartizare K, conturile 378 și 4428) care cer disciplină lunară de descărcare, spre deosebire de CMP unde fiecare ieșire se valorizează direct.

## Ce face iConta.eu

Cele două metode sunt module separate, alese explicit de utilizator, nu selectate automat de sistem. Modulul global-valoric (`core/stocuri.py`) ține mărfurile la preț de vânzare cu amănuntul, cu adaosul comercial separat în 378 și TVA neexigibilă în 4428, folosind coeficientul de repartizare K calculat lunar din rulaje cumulate. Modulul cantitativ-valoric (`core/stocuri_cv.py`) evaluează la cost mediu ponderat (CMP), recalculat după fiecare intrare, cu fișă de magazie proprie pentru fiecare articol — nota de ieșire e direct 607=371 la valoarea CMP × cantitate, fără conturile 378/4428 și fără coeficient de repartizare.

Diferența practică cea mai vizibilă la finalul lunii: la global-valoric, descărcarea TVA din 4428 se face printr-o aproximare (cotă medie ponderată dedusă din structura stocului cumulat), nu din mixul real de cote vândute în lună — un cost administrativ suplimentar pe care CMP nu îl are, pentru că nu operează deloc cu 4428.

[iConta.eu](/)
