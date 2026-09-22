---
title: Cum se calculează adaosul la un magazin online?
description: Costul de achiziție al mărfii vândute online include și transportul plătit furnizorului la recepție, capitalizat proporțional pe liniile de marfă — abia după acest cost se calculează adaosul din diferența față de prețul de vânzare.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se calculează adaosul la un magazin online?

Un magazin online care aplică metoda global-valorică are o particularitate față de un magazin fizic: costurile de transport sunt aproape mereu prezente, fie la aducerea mărfii de la furnizor (intrare în gestiune), fie la livrarea către client (ieșire din gestiune — o operațiune complet separată de adaosul comercial). Doar transportul de intrare intră în calculul costului de achiziție și, implicit, al adaosului.

## Temeiul legal

::: ghid-temei
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

> "(8) [...] costul bunurilor vândute se calculează prin deducerea valorii marjei brute din prețul
> de vânzare al stocurilor. Orice modificare a prețului de vânzare presupune recalcularea marjei
> brute."
>
> — sursă: `anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`, pct. 286 alin. (8).
:::

## Transport la intrare vs. transport la ieșire

Transportul plătit către furnizor pentru aducerea mărfii în depozit (transport de intrare) e cheltuială direct atribuibilă achiziției și intră în costul de achiziție — deci reduce adaosul rezultat, dacă prețul de vânzare rămâne neschimbat. Transportul facturat clientului la livrarea comenzii (transport de ieșire, curierat) e o prestare de serviciu separată, facturată de regulă distinct, care nu are legătură cu calculul adaosului comercial pe marfa vândută.

::: ghid-exemplu
Un magazin online recepționează 50 de produse la 40 lei/buc (preț achiziție fără TVA), plus 200 lei transport de la furnizor pentru întreaga comandă. Transportul se repartizează proporțional pe cele 50 de produse: 200/50 = 4 lei/buc. Cost de achiziție per produs = 40 + 4 = 44 lei.

Dacă produsul se vinde online la 79 lei (cu TVA 21% inclus): TVA extras = 79 × 21/121 ≈ 13,71 lei; adaos = 79 − 13,71 − 44 ≈ 21,29 lei.

Costul de livrare către client (curierat, facturat separat la 15 lei) nu intră în acest calcul — e o prestare de serviciu distinctă, nu parte din costul mărfii.
:::

## Ce se greșește în practică

- Se include costul de livrare către client în costul de achiziție al mărfii, micșorând artificial adaosul comercial calculat.
- Se omite capitalizarea transportului de la furnizor, tratându-l direct ca o cheltuială de exploatare a lunii, deși legea cere atribuirea lui direct costului mărfii.
- Se repartizează transportul de intrare în mod egal pe toate liniile NIR, indiferent de cantitate sau valoare, deși o repartizare proporțională (pe cantitate sau valoare) reflectă mai corect costul real per produs.
- Se schimbă prețul de vânzare online frecvent (promoții, ajustări de piață) fără să se recalculeze și să se reflecte contabil noua marjă, deși legea cere recalcularea marjei brute la fiecare modificare de preț.

## Ce face iConta.eu

La recepția (NIR) unui magazin online, `nir_gv` calculează costul de bază al fiecărei linii (cantitate × preț achiziție, fără TVA), la care adaugă partea proporțională din transport și taxe declarate la nivelul întregului NIR — capitalizate, adică incluse în costul de achiziție, nu tratate ca cheltuială separată. Repartizarea se face proporțional pe linii, cu restul de rotunjire alocat pe ultima linie, pentru ca suma repartizată să corespundă exact cu totalul transportului plătit. Din prețul de vânzare (cu TVA inclus) se extrage TVA prin formula sutei mărite, iar adaosul rezultă ca diferență între vânzare, TVA și costul de achiziție (deja cu transport capitalizat).

Transportul facturat clientului la livrarea comenzii nu face parte din acest calcul — e o prestare de serviciu separată de vânzarea mărfii, tratată distinct în contabilitate, nu ca parte a costului de achiziție al produsului vândut.

[iConta.eu](/)
