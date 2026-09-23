---
title: Ce este contul 378 și cum se folosește?
description: Contul 378 „Diferențe de preț la mărfuri” ține evidența adaosului comercial din gestiunea la preț cu amănuntul — se creditează cu adaosul aferent mărfurilor intrate și se debitează cu adaosul aferent mărfurilor ieșite, iar soldul arată adaosul rămas în stocul de la sfârșitul perioadei.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce este contul 378 și cum se folosește?

Contul 378 „Diferențe de preț la mărfuri” nu ține evidența unei datorii sau a unei creanțe, ci a unei componente a valorii mărfurilor din gestiune: adaosul comercial (marja comerciantului), pentru firmele care țin evidența mărfurilor la preț cu amănuntul (metoda global-valorică). E un cont rectificativ al valorii de înregistrare a mărfurilor din contul 371, nu un cont independent.

## Temeiul legal

::: ghid-temei
„Contul 378 «Diferențe de preț la mărfuri» ... Cu ajutorul acestui cont se ține evidența adaosului comercial (marja comerciantului) aferent mărfurilor din unitățile comerciale.” În credit — adaosul aferent mărfurilor intrate (371); în debit — adaosul aferent mărfurilor ieșite (371). „Soldul contului reprezintă valoarea adaosului comercial aferent mărfurilor existente în stoc la sfârșitul perioadei.”

— *OMFP 1802/2014, Capitolul 16, funcțiunea contului 378.*

„... pentru determinarea costului pot fi folosite, de asemenea, ... metoda prețului cu amănuntul, în comerțul cu amănuntul.”

— *OMFP 1802/2014, pct. 286 alin. (1).*
:::

## Cum funcționează, în practică

- **La intrarea mărfii** (recepție/NIR), pe lângă costul de achiziție (371 = 401) și TVA-ul deductibil (4426 = 401), se înregistrează separat adaosul comercial stabilit de firmă: `371 = 378`.
- **La ieșirea mărfii prin vânzare** (descărcare de gestiune, de regulă lunară), adaosul aferent mărfii vândute se scoate din 378, proporțional cu vânzările lunii: `378 = 371`.
- **Soldul contului 378**, la orice moment, reprezintă adaosul comercial aferent mărfurilor rămase încă nevândute în stoc — nu adaosul total încasat de la începutul anului, ci doar partea „blocată” în stocul curent.

Contul 378 nu se folosește izolat — el intră, împreună cu 371 (mărfuri, la valoarea de înregistrare) și 4428 (TVA neexigibilă), în formula coeficientului de repartizare care determină, lunar, cât din vânzări reprezintă cost de achiziție și cât adaos.

## Ce se greșește în practică

- Se tratează 378 ca pe un cont de venituri sau de rezultat, calculând „profitul” direct din soldul lui — 378 arată doar adaosul rămas în stoc, nu adaosul realizat prin vânzări (acela apare descărcat prin nota lunară, nu în soldul contului).
- Se folosește 378 și la firmele care țin gestiunea cantitativ-valoric (evidență pe articol, cu preț de achiziție), unde adaosul nu se separă pe un cont distinct — 378 e specific metodei global-valorice, la preț cu amănuntul.
- Se omite înregistrarea adaosului la intrare (371=378), ceea ce face imposibil calculul corect al coeficientului de repartizare la descărcarea lunară.

## Ce face iConta.eu

Motorul de gestiune global-valorică, `core/stocuri.py`, folosește explicit contul 378 în ambele funcții relevante: la recepție (`nir_gv`), nota propusă include linia `371=378` pentru adaosul stabilit pe fiecare articol; la descărcarea lunară (`descarcare_gv`), soldul și rulajul contului 378 (`Si378`, `Rc378`) intră direct în formula coeficientului K, iar nota de descărcare produce linia `378=371` pentru adaosul aferent vânzărilor lunii. Rulajele contului 378 sunt citite din notele **validate** (`status='validata'`), cumulat de la 1 ianuarie, exact cum cere calculul legal al coeficientului de repartizare.

[iConta.eu](/)
