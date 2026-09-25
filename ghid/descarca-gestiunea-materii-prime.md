---
title: "Cum se descarcă gestiunea pentru materii prime?"
description: "Metodele acceptate de evaluare la ieșirea din gestiune a stocurilor de materii prime, conform reglementărilor contabile OMFP 1802/2014."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se descarcă gestiunea pentru materii prime?

„Descărcarea gestiunii" înseamnă scoaterea din evidența contabilă a bunurilor la ieșire — consum în producție, vânzare, transfer — la o valoare stabilită după o metodă legală de evaluare, nu la o valoare aleasă ad-hoc. Reglementările contabile prevăd exact ce metode sunt acceptate și cum se aplică fiecare.

## Temeiul legal

::: ghid-temei
„95. - (1) La data ieșirii din entitate sau la darea în consum, bunurile se evaluează și se scad din gestiune la valoarea lor de intrare sau valoarea la care sunt înregistrate în contabilitate [...]. 96. - (1) Costul de achiziție sau costul de producție al stocurilor din aceeași categorie și al tuturor elementelor fungibile se calculează prin aplicarea uneia din următoarele metode: a) metoda costului mediu ponderat - CMP; [...] b) metoda primul intrat-primul ieșit - FIFO; [...] c) metoda ultimul intrat-primul ieșit - LIFO."
— OMFP 1802/2014 (reglementările contabile), pct. 95 alin. (1) și pct. 96 alin. (1) (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

Detaliile metodelor, conform aceluiași punct 96:

- **CMP (cost mediu ponderat)**: costul fiecărui element ieșit din gestiune se calculează pe baza mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei, plus costul elementelor intrate în timpul perioadei. Media poate fi recalculată periodic sau după fiecare recepție.
- **FIFO (primul intrat-primul ieșit)**: bunurile ieșite se evaluează la costul primei intrări (lot); pe măsura epuizării lotului, se trece la costul lotului următor, în ordine cronologică.
- **LIFO (ultimul intrat-primul ieșit)**: bunurile ieșite se evaluează la costul ultimei intrări; pe măsura epuizării, se trece la costul lotului anterior.

Pentru materii prime folosite în producție, oricare dintre aceste metode e legală — legea nu impune FIFO sau CMP în mod obligatoriu pentru categoria „materii prime" ca atare. Alegerea metodei e o politică contabilă a entității, care trebuie aplicată consecvent (principiul permanenței metodelor) și menționată în notele explicative ale situațiilor financiare.

## Ce se greșește în practică

- Se descarcă gestiunea la prețul de achiziție al ultimei facturi primite, indiferent de metoda declarată prin politicile contabile ale firmei — de fapt costul de ieșire trebuie calculat conform metodei alese (CMP, FIFO sau LIFO), nu după ultima factură.
- Se schimbă metoda de evaluare de la o lună la alta, în funcție de ce iese mai „convenabil" fiscal — încalcă principiul permanenței metodelor, care cere aplicare consecventă de la un exercițiu financiar la altul.
- Se confundă descărcarea de gestiune contabilă (scoaterea din stoc la costul de intrare) cu prețul de vânzare al produsului finit — sunt două evaluări diferite, una privind costul, cealaltă venitul.

## Ce face iConta.eu

La data acestui ghid, modulul de stocuri al iConta.eu implementează **metoda global-valorică (preț cu amănuntul)**, folosită tipic pentru mărfuri în comerț (NIR cu adaos comercial, coeficient K, descărcare lunară pe baza vânzărilor), conform OMFP 1802/2014. Aplicația nu implementează în prezent metodele cantitativ-valorice FIFO, CMP sau LIFO, care sunt cele relevante pentru evidența materiilor prime consumate în producție pe loturi sau costuri medii. Pentru firmele care gestionează materii prime cu aceste metode, descărcarea de gestiune trebuie calculată și înregistrată separat de contabil, în afara automatizării actuale a aplicației.

[iConta.eu](/)
