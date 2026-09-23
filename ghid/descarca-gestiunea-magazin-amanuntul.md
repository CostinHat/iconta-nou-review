---
title: Cum se descarcă gestiunea pentru un magazin cu amănuntul?
description: Pașii tehnici prin care iConta.eu calculează și propune nota de descărcare lunară de gestiune la metoda global-valorică.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se descarcă gestiunea pentru un magazin cu amănuntul?

La un magazin care ține evidența mărfurilor la preț cu amănuntul (metoda global-valorică), descărcarea de gestiune este operațiunea lunară prin care se determină, din vânzările efective ale lunii, cât reprezintă costul mărfii vândute, cât adaos comercial și cât TVA neexigibilă trebuie „scoase" din contul de mărfuri (371).

## Temeiul legal

::: ghid-temei
„... pentru determinarea costului pot fi folosite, de asemenea, metoda costului standard, în activitatea de producție sau metoda prețului cu amănuntul, în comerțul cu amănuntul."
— OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 286 alin. (1)
:::

## Cum funcționează, pas cu pas

1. **Pe parcursul lunii**, fiecare recepție de marfă (NIR) se înregistrează cu cotă de TVA obligatorie pe fiecare linie — aplicația refuză să presupună o cotă implicită, pentru ca o schimbare ulterioară de cotă legală să nu rămână „îngropată" într-o valoare scrisă cândva în cod. Costurile accesorii (transport, taxe) se capitalizează în costul de achiziție și se repartizează proporțional pe liniile recepției. Notele generate la recepție sunt ciorne: cost marfă (371=401), TVA deductibilă (4426=401), eventualele costuri accesorii, adaos (371=378) și TVA neexigibilă (371=4428).
2. **La finalul lunii**, se rulează descărcarea de gestiune pentru anul și luna respectivă. Aplicația calculează coeficientul K cumulat de la 1 ianuarie, din soldurile inițiale ale conturilor 371, 378 și 4428 (dacă există) și din rulajele reale ale acelorași conturi, citite din notele deja **validate** în jurnal.
3. **Vânzările lunii** (contul 707) sunt citite separat, filtrate pe sursele relevante de gestiune (case de marcat, stocuri, facturi de marfă) și numai pentru luna curentă, nu cumulat.
4. Din coeficientul K și vânzările lunii se calculează adaosul descărcat (K × vânzări), costul mărfii vândute (vânzări minus adaos) și TVA neexigibilă aferentă vânzărilor. Dacă în luna respectivă nu au existat vânzări, aplicația nu generează nicio notă.
5. Aplicația **propune** nota de descărcare ca ciornă, datată la ultima zi calendaristică a lunii — contabilul verifică și validează manual, moment după care nota nu mai poate fi editată sau ștearsă din aplicație.

## Ce se greșește în practică

- Se rulează descărcarea înainte ca toate recepțiile lunii să fie validate în jurnal — rulajele necontabilizate încă nu intră în calculul coeficientului K.
- Se validează nota fără verificarea prealabilă a coeficientului K rezultat, deși aceasta este ultima ocazie de corecție ușoară, înainte ca nota să devină nemodificabilă.

## Ce face iConta.eu

Calculul e complet automatizat pe baza soldurilor și rulajelor reale, iar aplicația refuză explicit să calculeze dacă rezultatul ar fi matematic imposibil (numitor zero sau negativ, cost al mărfii vândute negativ) — în loc să propună o notă cu o valoare implicită greșită. Descărcarea rămâne propunere (ciornă) până la validarea manuală a contabilului, care păstrează controlul final asupra jurnalului.

[iConta.eu](/)
