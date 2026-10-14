---
title: "Cum reconciliez D394 cu D300?"
description: "De ce D300 și D394 nu sunt declarații egale, ce include fiecare și cum verifică practic un contabil coerența dintre ele, folosind reconcilierea internă a D394."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum reconciliez D394 cu D300?

D300 și D394 nu declară aceleași operațiuni, deci nu trebuie să coincidă cifră cu cifră — relația dintre ele e de **incluziune**, nu de egalitate. D300 conține tot TVA-ul firmei, inclusiv operațiunile intracomunitare și importurile; D394 conține doar operațiunile pe teritoriul național, cu achizițiile intracomunitare excluse explicit. Reconcilierea reală înseamnă să știi ce subset compari, nu să cauți o potrivire totală.

## Temeiul legal

::: ghid-temei
„Nu se înscriu achiziţiile intracomunitare de bunuri şi servicii pentru care există obligativitatea înscrierii în declaraţia 390."
— OPANAF 2194/2025 (Anexa 2 pct.1 lit.b, care modifică Anexa 2 a OPANAF 3769/2015), aplicabil operațiunilor derulate de la 1.08.2025 (sursă: [OPANAF nr. 2194/2025 pentru modificarea OPANAF nr. 3769/2015 (declarația informativă D394)](https://legislatie.just.ro/Public/DetaliiDocument/302310))
:::

Ce rezultă practic pentru o reconciliere corectă:

- **Achizițiile intracomunitare de bunuri și servicii NU intră niciodată în D394** — ele se declară exclusiv în D390. O diferență la acest capitol între D300 și D394 nu e o eroare, e comportamentul așteptat.
- **Livrările intracomunitare, în schimb, INTRĂ în D394** — apar ca tip L, reclasificat LS (livrare scutită) la cotă 0, la fel ca exporturile. Doar direcția „achiziție" de la un partener UE/non-UE e exclusă din D394, nu și „livrare".
- D300 include, în plus față de D394, toate operațiunile intracomunitare și de import (rândurile dedicate IC/import), pe când D394 acoperă doar operațiunile interne raportabile (livrări/achiziții/prestări cu parteneri identificați prin CUI, inclusiv taxare inversă internă).
- Periodicitatea celor două declarații e **identică** (perioada fiscală declarată pentru decontul de TVA — lunar/trimestrial/semestrial/anual), deci fereastra de comparat e aceeași lună/trimestru pentru amândouă.

## Ce se greșește în practică

- Se așteaptă ca baza de TVA colectată/dedusă din D300 să fie egală cu totalul operațiunilor din D394, ignorând că D300 conține și operațiuni (IC, import) pe care D394 nu le are deloc.
- Se raportează ca „eroare" absența achizițiilor intracomunitare din D394, când de fapt legea le exclude explicit — locul lor e D390, nu D394.
- Se compară D394 cu D300 pe perioade diferite (de exemplu D300 lunar vs. o fereastră trimestrială greșit aliniată), fără să se verifice că periodicitatea celor două e sincronizată cu vectorul fiscal al firmei.

## Ce face iConta.eu

iConta.eu **nu are un ecran sau un raport de reconciliere „D394 vs. D300"**, dar cele două declarații pornesc din aceleași date și din aceleași calcule. TVA-ul dedus pe facturile cu TVA la încasare achitate în perioadă intră în D394 calculat exact ca în D300 — pe aceleași facturi și cu aceeași alocare pe cote. Facturile anulate/stornate pe care D300 le exclude sunt excluse și din D394. Aplicația nu cere ca totalurile să fie egale (TVA colectată din D300 ≥ livrările din D394 pe aceeași cotă, fiindcă D300 e TVA totală, iar D394 doar subsetul raportabil), iar concordanța dintre TVA pe cotă din D300 și din D394 este verificată la fiecare actualizare a aplicației.

Ce nu există e o reconciliere **de business**, afișată contabilului la generare, care să verifice că diferența dintre cele două declarații se explică exclusiv prin operațiunile IC excluse din D394 — verificările de concordanță de mai sus sunt interne aplicației, nu un ecran sau un raport pe care contabilul îl vede.

Ce are aplicația, pentru D394 în sine, sunt două verificări independente înainte de depunere: validarea prin **DUKIntegrator** (validatorul oficial ANAF, rulat local) și o **a doua cale de calcul**, care recalculează independent totalurile pe cotă direct din liniile brute ale facturilor și **oprește generarea** dacă diferă de rezultatul calculului principal. Această a doua verificare are limite: nu acoperă operațiunile manuale (bonuri/borderouri, azi fără ecran propriu) și nu prinde o eroare pe care ambele căi de calcul o fac identic (de exemplu o cotă de TVA tastată greșit o singură dată, pe factură). Reconcilierea propriu-zisă cu D300 — verificarea că diferența dintre cele două declarații se explică exclusiv prin operațiunile IC excluse din D394 — rămâne, azi, o verificare manuală a contabilului.

[iConta.eu](/)
