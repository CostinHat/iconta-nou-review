---
title: "Cum se calculează costul de producție la un meniu"
description: Costul unui preparat se calculează la costul mediu ponderat al ingredientelor din stoc, la data vânzării — metoda impusă de reglementările contabile, nu una aleasă liber de fiecare restaurant.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se calculează costul de producție la un meniu

Costul unui preparat (un „meniu" sau o rețetă) se obține însumând costul ingredientelor consumate pentru porțiile vândute, evaluate la costul mediu ponderat (CMP) al fiecărui ingredient în stoc, la data la care sunt scoase din gestiune.

## Temeiul legal

::: ghid-temei
„Costul de achiziție sau costul de producție al stocurilor din aceeași categorie și al tuturor elementelor fungibile se calculează prin aplicarea uneia din următoarele metode: a) metoda costului mediu ponderat — CMP [...] Metoda «costului mediu ponderat» (CMP) presupune calcularea costului fiecărui element pe baza mediei ponderate a costurilor elementelor similare aflate în stoc la începutul perioadei și a costului elementelor similare produse sau cumpărate în timpul perioadei." — OMFP nr. 1802/2014, pct. 96 alin. (1) lit. a) și alin. (2)
:::

Legea permite recalcularea CMP fie periodic, fie după fiecare recepție de marfă — sunt două variante legal valabile, nu una singură impusă.

## Cum se calculează, practic

Pentru fiecare preparat, rețeta stabilește cantitatea de ingredient necesară pe porție. La vânzarea a N porții:

1. se ia costul mediu ponderat curent al fiecărui ingredient, calculat din fișa de magazie (intrări și ieșiri cronologice);
2. se înmulțește cantitatea/porție × numărul de porții × CMP-ul ingredientului, pentru fiecare ingredient din rețetă;
3. suma costurilor tuturor ingredientelor dă costul total al preparatului pentru porțiile vândute — din care rezultă și costul/porție și procentul de food cost (cost ingrediente ÷ preț de vânzare fără TVA).

Costul rezultat depinde direct de CMP-ul din acel moment — dacă prețurile de achiziție ale ingredientelor variază, costul aceleiași rețete variază și el de la o vânzare la alta.

## Ce se greșește în practică

- Se calculează costul rețetei o singură dată, la introducerea ei, și se păstrează fix — fără să se țină cont că CMP-ul ingredientelor se schimbă la fiecare intrare nouă de marfă.
- Se confundă costul de producție (costul ingredientelor consumate) cu prețul de vânzare sau cu marja — sunt trei cifre diferite, chiar dacă se calculează din aceleași date.
- Se ignoră data exactă a vânzării la calculul CMP — costul corect e cel valabil la data consumului, nu cel curent la momentul verificării ulterioare.

## Ce face iConta.eu

Din cardul „Rețete (HoReCa)" al ecranului Stocuri, introduci ingredientele și cantitatea/porție pentru fiecare preparat. La „descărcarea" unei rețete (înregistrarea vânzării a N porții), aplicația calculează automat costul mediu ponderat al fiecărui ingredient la data operațiunii, generează mișcările de ieșire din stoc și o notă contabilă ciornă, și afișează costul total, costul/porție și procentul de food cost. Verificarea cronologică incorporată împiedică o ieșire înregistrată cu dată anterioară să „spargă" soldurile deja calculate ale mișcărilor ulterioare.

[iConta.eu](/)
