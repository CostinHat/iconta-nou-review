---
title: Ce fac dacă am omis adaosul comercial la amănunt?
description: Adaosul comercial nu se introduce separat, ci rezultă automat din diferența dintre prețul de vânzare și costul de achiziție — dacă a fost „omis”, de regulă înseamnă că prețul de vânzare a fost setat greșit, egal sau sub costul de achiziție.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Ce fac dacă am omis adaosul comercial la amănunt?

La metoda global-valorică, adaosul comercial nu e un câmp separat pe care contabilul îl completează — e rezultatul aritmetic al diferenței dintre prețul de vânzare cu amănuntul (din care se extrage TVA) și costul de achiziție. Dacă „s-a omis” adaosul, în practică înseamnă unul din două lucruri: fie prețul de vânzare a fost introdus egal cu costul (adaos zero, dar valid), fie prețul a fost introdus sub cost, caz în care operațiunea a fost respinsă chiar de la introducere.

## Temeiul legal

::: ghid-temei
> "286. - [...] (8) În comerțul cu amănuntul poate fi utilizată metoda prețului cu amănuntul,
> pentru a determina costul stocurilor de articole numeroase și cu mișcare rapidă, care au marje
> similare și pentru care nu este practic să se folosească altă metodă. În această situație,
> **costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul de
> vânzare al stocurilor**. Orice modificare a prețului de vânzare presupune recalcularea marjei
> brute."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 286 alin. (8).

> "Contul 378 «Diferențe de preț la mărfuri» [se ține pentru] evidența **adaosului comercial (marja
> comerciantului)** aferent mărfurilor din unitățile comerciale. Contul 378 [...] este un **cont
> rectificativ al valorii de înregistrare a mărfurilor**. În creditul contului 378 [...] se
> înregistrează: – valoarea adaosului comercial aferent mărfurilor intrate în gestiune (371). În
> debitul contului 378 [...] se înregistrează: – valoarea adaosului comercial aferent mărfurilor
> ieșite din gestiune (371). Soldul contului reprezintă valoarea adaosului comercial aferent
> mărfurilor existente în stoc la sfârșitul perioadei."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt` — funcțiunea contului 378
> (grupa 37 "Mărfuri").
:::

## Ce spune legea despre vânzarea fără marjă sau sub cost

Legea nu obligă existența unui adaos pozitiv la fiecare articol. Contul 378 e definit ca „rectificativ” al valorii mărfii — nu are un sold obligatoriu creditor la fiecare linie. O vânzare cu marjă zero e legal posibilă (deși neobișnuită comercial). O vânzare sub costul de achiziție e, de asemenea, o decizie comercială legitimă — lichidare de stoc, produs cu termen de valabilitate aproape de expirare — și legea nu o interzice.

## Ce se greșește în practică

- Se introduce prețul de vânzare cu amănuntul fără să se includă și marja dorită, ci doar cost + TVA — rezultă adaos zero, deși comerciantul credea că a stabilit un adaos.
- Se încearcă „adăugarea” ulterioară a unui adaos la un NIR deja validat, editând direct nota contabilă — o dată validat, NIR-ul nu ar trebui modificat retroactiv, ci corectat printr-o operațiune separată, discutată cu dezvoltatorul aplicației.
- Se confundă refuzul aplicației la vânzare sub cost cu o interdicție legală — de fapt e o gardă de business împotriva erorilor de tastare la prețuri, nu o normă contabilă impusă de OMFP 1802/2014.
- Se schimbă prețul de raft fără să se recalculeze marja și fără să se reflecte schimbarea în contabilitate, deși legea cere recalcularea marjei brute la orice modificare a prețului de vânzare.

## Ce face iConta.eu

La fiecare linie de NIR, `nir_gv` calculează automat adaosul ca diferență între prețul de vânzare (cu TVA extras prin formula sutei mărite) și costul de achiziție. Dacă rezultatul e negativ — adică prețul de vânzare introdus e sub costul de achiziție — aplicația ridică eroare și refuză înregistrarea; adaosul zero, în schimb, e permis (nu există verificare separată care să blocheze un adaos de exact 0).

Dacă un NIR a fost deja validat cu un preț de vânzare greșit (implicit cu adaosul dorit „omis”), corecția nu ar trebui făcută prin editarea directă a notei validate — NIR-urile trec prin stadiul de ciornă, cu „validare ulterioară de către contabil”, tocmai pentru a păstra trasabilitatea operațiunilor. Pentru un NIR deja validat cu date greșite, corecția exactă (ce operațiune anume se face) e de stabilit împreună cu dezvoltatorul aplicației, nu presupusă — nu e o cerință impusă direct de OMFP 1802/2014.

[iConta.eu](/)
