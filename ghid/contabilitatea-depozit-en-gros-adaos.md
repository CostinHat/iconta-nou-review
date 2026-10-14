---
title: "Contabilitatea unui depozit en-gros: adaos și descărcare"
description: "De ce metoda global-valorică (preț cu amănuntul) nu se potrivește, de regulă, unui depozit cu vânzare en-gros, și spre ce evidență se orientează astfel de gestiuni."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Contabilitatea unui depozit en-gros: adaos și descărcare

Titlul cere aplicarea mecanismului de adaos și descărcare (metoda global-valorică) la un depozit cu vânzare en-gros. Trebuie spus onest: legea leagă explicit metoda prețului cu amănuntul de **comerțul cu amănuntul**, nu de vânzarea cu ridicata (en-gros), și o rezervă pentru stocuri de articole numeroase, cu mișcare rapidă și marje similare.

## Temeiul legal

::: ghid-temei
„În funcție de specificul activității, pentru determinarea costului pot fi folosite, de asemenea, metoda costului standard, în activitatea de producție sau metoda prețului cu amănuntul, în comerțul cu amănuntul."
— OMFP 1802/2014, Anexa 1, pct. 286 alin. (1) (sursă: [OMFP nr. 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate)](https://legislatie.just.ro/Public/DetaliiDocument/164320))

„În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul, pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje similare și pentru care nu este practic să se folosească altă metodă. În această situație, costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul de vânzare al stocurilor. Orice modificare a prețului de vânzare presupune recalcularea marjei brute."
— OMFP 1802/2014, Anexa 1, pct. 286 alin. (8) (sursă: [OMFP nr. 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate)](https://legislatie.just.ro/Public/DetaliiDocument/164320))

„Coeficienții de repartizare a diferențelor de preț pot fi calculați la nivelul conturilor sintetice de gradul I și II, prevăzute în Planul de conturi general, pe grupe sau categorii de stocuri."
— OMFP 1802/2014, Anexa 1, pct. 286 alin. (5) (sursă: [OMFP nr. 1802/2014 (Reglementările contabile privind situațiile financiare anuale individuale și consolidate)](https://legislatie.just.ro/Public/DetaliiDocument/164320))
:::

Textul legal condiționează explicit metoda prețului cu amănuntul de comerțul **cu amănuntul**. Un depozit en-gros vinde, prin definiție, cu ridicata — de regulă către alți comercianți, nu către consumatorul final, la un preț de vânzare fix afișat la raft. Cerința de la pct. 286 alin. (8) — „articole numeroase și cu mișcare rapidă, care au marje similare, pentru care nu este practic să se folosească altă metodă" — descrie profilul unui magazin cu amănuntul, nu al unei relații de vânzare en-gros, unde prețul și marja se negociază de regulă pe client sau pe tranzacție.

## Când profilul se apropie de amănunt și când nu

Dacă depozitul vinde efectiv pe un preț de listă unic (catalog, listă de prețuri standard, marje similare pe categorii de produse) — de exemplu un depozit de tip cash & carry — profilul vânzării se apropie de cel descris la alin. (8). Dacă entitatea alege totuși metoda global-valorică (decizie de politică contabilă, de motivat față de textul care vorbește de comerțul cu amănuntul), mecanismul e același ca la un magazin: fiecare recepție intră în 371/378/4428 la prețul de listă, iar descărcarea lunară repartizează adaosul și TVA prin coeficientul K — eventual calculat pe grupe/categorii de stocuri (alin. (5)), dacă depozitul are linii de produse cu marje foarte diferite.

Dacă însă prețurile variază semnificativ per client sau contract (rabaturi negociate, prețuri diferite pentru cantități mari), premisa „marje similare" nu se mai verifică — costul mărfii ieșite nu mai poate fi dedus corect dintr-un singur preț de vânzare, iar evidența cantitativ-valorică (cost mediu ponderat sau FIFO, pe fiecare articol) reflectă mai fidel realitatea.

## Ce se greșește în practică

- Se aplică automat metoda global-valorică (cu conturile 378 „Diferențe de preț" și 4428 „TVA neexigibilă") la un depozit en-gros doar pentru că firma vinde marfă cu adaos. Metoda presupune un preț de vânzare fix, afișat, pe stoc — o premisă care de regulă nu se potrivește vânzării cu ridicata.
- Se amestecă, în același coeficient K, marfă vândută la preț de listă cu marfă vândută cu rabat negociat per client — coeficientul rezultat nu mai reflectă corect nicio categorie.
- Se ignoră posibilitatea de a calcula coeficienți separați pe grupe/categorii de stocuri (alin. (5)), deși legea o permite explicit, atunci când stocul are linii de produse cu marje foarte diferite.

## Ce face iConta.eu

Pentru gestiuni pe cantități și costuri individuale — mai apropiate de profilul unui depozit en-gros — iConta.eu are, în ecranul Stocuri, evidența cantitativ-valorică la cost mediu ponderat: recalculează costul mediu ponderat după fiecare intrare, ține o fișă de magazie cronologică per articol și nu permite unei ieșiri să depășească stocul existent la data ei.

Pentru metoda global-valorică, NIR-ul global-valoric din ecranul Stocuri calculează costul de achiziție (cu transport și taxe capitalizate), extrage TVA din prețul de vânzare prin formula sutei mărite și calculează adaosul, respingând adaosul negativ sau vânzarea sub cost; la descărcarea lunară, coeficientul K poate fi rulat separat pe grupe/categorii de stocuri, dacă rulajele sunt separate corespunzător. Calculul nu distinge între „magazin cu amănuntul" și „depozit en-gros" — lucrează cu prețurile, costurile și cotele de TVA introduse la fiecare linie de NIR. TVA descărcată lunar din 4428 rămâne o aproximare dintr-o cotă medie ponderată a stocului cumulat, nu din structura reală a vânzărilor lunii — de verificat separat, mai ales dacă depozitul lucrează cu produse la cote de TVA diferite.

Aplicația nu alege metoda în locul contabilului: încadrarea unui depozit en-gros concret într-una din cele două evidențe e o decizie de politică contabilă a entității, de luat în funcție de modul real de stabilire a prețurilor de vânzare.

[iConta.eu](/)
