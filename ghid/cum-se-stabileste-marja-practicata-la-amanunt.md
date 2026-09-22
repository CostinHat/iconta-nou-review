---
title: Cum se stabilește marja practicată la amănunt?
description: La metoda global-valorică marja (adaosul comercial) nu se introduce separat, ci rezultă din diferența dintre prețul de vânzare cu amănuntul și costul de achiziție, cu TVA extras din preț prin formula sutei mărite.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se stabilește marja practicată la amănunt?

La metoda prețului cu amănuntul, costul mărfii vândute se obține prin deducerea marjei brute din prețul de vânzare — nu invers. Practic, comerciantul nu „calculează” adaosul plecând de la cost și un procent dorit, ci stabilește prețul de vânzare cu amănuntul, iar adaosul (diferența de preț) rezultă automat din compararea acestui preț cu costul de achiziție.

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

> "6. cost de achiziție înseamnă prețul datorat și eventualele cheltuieli conexe minus eventualele
> reduceri ale costului de achiziție. În acest sens, **costul de achiziție al bunurilor cuprinde
> prețul de cumpărare, taxele de import și alte taxe (cu excepția acelora pe care persoana juridică
> le poate recupera de la autoritățile fiscale), cheltuielile de transport, manipulare și alte
> cheltuieli care pot fi atribuibile direct achiziției bunurilor respective**. În costul de
> achiziție se includ, de asemenea, comisioanele, taxele notariale, cheltuielile cu obținerea de
> autorizații și alte cheltuieli nerecuperabile, atribuibile direct bunurilor respective.
> Cheltuielile de transport sunt incluse în costul de achiziție și atunci când funcția de
> aprovizionare este externalizată."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 8, definiții, poziția 6
> ("cost de achiziție").
:::

## Formula practică a marjei

Adaosul comercial la o linie de NIR se obține astfel: din prețul de vânzare cu amănuntul (care include TVA) se extrage TVA prin formula sutei mărite, apoi se scade costul de achiziție (inclusiv transportul și taxele capitalizate). Ce rămâne este marja brută — adaosul.

::: ghid-exemplu
Marfă cu cost de achiziție 100 lei/buc (deja cu transport inclus), vândută cu amănuntul la 169 lei/buc, cotă TVA 21%:
- TVA extras din preț: 169 × 21/121 ≈ 29,33 lei;
- adaos = 169 − 29,33 − 100 = 39,67 lei.

Dacă în schimb comerciantul stabilește prețul de vânzare la exact 121 lei (cost 100 + TVA calculat pe cost), adaosul rezultat este 0 — corect din punct de vedere aritmetic, dar înseamnă vânzare fără marjă comercială.
:::

## Ce se greșește în practică

- Se stabilește prețul de vânzare adăugând TVA direct la cost, fără a include și marja dorită — rezultă adaos zero, deși comerciantul crede că a aplicat un adaos.
- Se calculează adaosul „pe cost” (cost × procent), apoi se adaugă TVA separat, deși prețul afișat clientului trebuie să conțină deja TVA — riscul e ca prețul final afișat să nu corespundă cu ce a fost efectiv introdus în NIR.
- Se schimbă prețul de vânzare pe raft fără să se recalculeze și să se înregistreze contabil noua marjă, deși legea cere recalcularea marjei brute la orice modificare de preț.
- Se omite din costul de achiziție transportul sau alte taxe nerecuperabile, ceea ce umflă artificial adaosul calculat.

## Ce face iConta.eu

La recepția în regim global-valoric, `nir_gv` calculează mai întâi costul de achiziție al fiecărei linii (cantitate × preț achiziție, plus partea proporțională din transport și taxe capitalizate, cu restul de rotunjire alocat pe ultima linie). Pentru prețul de vânzare introdus (cu TVA inclus), funcția extrage TVA prin formula sutei mărite (`tva = vanz × cota/(100+cota)`), apoi calculează adaosul ca diferență între vânzare, TVA și cost. Dacă prețul de vânzare introdus e sub costul de achiziție, sau dacă adaosul rezultat ar fi negativ, aplicația refuză operațiunea — o gardă împotriva erorilor de tastare la introducerea prețurilor, nu o interdicție impusă de lege.

[iConta.eu](/)
