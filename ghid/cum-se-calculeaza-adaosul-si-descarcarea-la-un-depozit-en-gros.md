---
title: Cum se calculează adaosul și descărcarea la un depozit en-gros?
description: Metoda global-valorică este definită de lege pentru comerțul cu amănuntul, deci un depozit en-gros trebuie să verifice dacă profilul activității (articole numeroase, marje similare, preț de vânzare unic) se potrivește criteriilor legale înainte de a o aplica.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează adaosul și descărcarea la un depozit en-gros?

Metoda prețului cu amănuntul (global-valorică) e definită de lege special pentru comerțul cu amănuntul, pentru stocuri de articole numeroase, cu mișcare rapidă și marje similare — practic, vânzare la un preț de listă/raft. Un depozit en-gros vinde de regulă pe bază de contract sau negociere per client, cu prețuri diferite pentru cantități sau parteneri diferiți. Înainte de a aplica mecanismul global-valoric la un depozit en-gros, merită verificat dacă activitatea se încadrează efectiv în criteriile legale, sau dacă evidența cantitativ-valorică e alegerea mai potrivită.

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

> "(5) Coeficienții de repartizare a diferențelor de preț pot fi calculați la nivelul conturilor
> sintetice de gradul I și II, [...] pe grupe sau categorii de stocuri."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 286 alin. (5).
:::

## Când se potrivește și când nu

Dacă depozitul en-gros vinde efectiv pe un preț de listă unic (catalog, listă de prețuri standard, marje similare pe categorii de produse) — de exemplu un depozit de tip cash & carry — mecanismul global-valoric se aplică identic ca la un magazin cu amănuntul: fiecare recepție intră în 371/378/4428 la prețul de listă, iar descărcarea lunară repartizează adaosul și TVA prin coeficientul K, eventual calculat pe grupe/categorii de stocuri conform pct. 286 alin. (5), dacă depozitul are linii de produse cu marje foarte diferite.

Dacă însă prețurile variază semnificativ per client sau contract (rabaturi negociate, prețuri en-gros diferite pentru cantități mari), premisa „marje similare” de la alin. (8) nu se mai verifică — costul mărfii ieșite nu mai poate fi dedus corect dintr-un singur preț de vânzare „de amănuntul”, iar evidența cantitativ-valorică (cost mediu ponderat sau FIFO, pe fiecare articol) reflectă mai fidel realitatea.

## Ce se greșește în practică

- Se aplică mecanic metoda global-valorică unui depozit en-gros doar pentru că „așa se face la stocuri”, fără să se verifice dacă vânzările au efectiv un preț unic de listă.
- Se amestecă, în același coeficient K, marfă vândută la preț de listă cu marfă vândută cu rabat negociat per client — coeficientul rezultat nu mai reflectă corect nicio categorie.
- Se ignoră posibilitatea de a calcula coeficienți separați pe grupe/categorii de stocuri (alin. 5), deși legea o permite explicit, atunci când depozitul are linii de produse cu marje foarte diferite.
- Se presupune că un depozit en-gros nu poate niciodată folosi metoda global-valorică — de fapt, criteriul legal e profilul vânzării (preț unic, articole numeroase, marje similare), nu tipul de client (persoană fizică vs. comerciant).

## Ce face iConta.eu

Mecanismul de calcul din `core/stocuri.py` nu distinge tehnic între „magazin cu amănuntul” și „depozit en-gros” — motorul lucrează cu prețuri de vânzare, costuri de achiziție și cote de TVA introduse explicit la fiecare linie de NIR, indiferent de tipul de client final. `nir_gv` calculează costul de achiziție (cu transport și taxe capitalizate), extrage TVA din prețul de vânzare prin formula sutei mărite și calculează adaosul, respingând adaos negativ sau vânzare sub cost. La descărcarea lunară, `coeficient_k` poate fi rulat separat pe grupe/categorii de stocuri, dacă rulajele sunt separate corespunzător — util pentru un depozit cu linii de produse cu marje foarte diferite.

Decizia dacă un depozit en-gros se încadrează efectiv în criteriile legale ale metodei prețului cu amănuntul (preț de vânzare unic, marje similare) rămâne una de politică contabilă a entității, nu una impusă tehnic de aplicație. Iar dacă metoda e aplicată, TVA-ul descărcat lunar din 4428 rămâne o aproximare dintr-o cotă medie ponderată a stocului cumulat, nu din structura reală a vânzărilor lunii — de verificat separat, mai ales dacă depozitul lucrează cu produse la cote de TVA diferite.

[iConta.eu](/)
