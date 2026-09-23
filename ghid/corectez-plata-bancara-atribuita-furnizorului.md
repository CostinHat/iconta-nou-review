---
title: "Cum corectez o plată bancară atribuită furnizorului greșit?"
description: Calea de corectare depinde de starea notei generate de reconciliere — dacă e încă ciornă se poate șterge direct, dacă a fost deja validată, corectarea se face printr-o dezlegare explicită, cu motiv, doar dacă luna contabilă e încă deschisă.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum corectez o plată bancară atribuită furnizorului greșit?

Când reconcilierea bancară alocă automat o plată pe facturile unui alt furnizor decât cel real, corectarea se face diferit în funcție de starea în care se află nota contabilă generată — ciornă sau deja validată.

## Temeiul legal

::: ghid-temei
„Erorile se corectează prin tăierea cu o linie a textului sau a cifrei greșite, concomitent înscriindu-se alături textul sau cifra corectă. Corectarea se face în toate exemplarele documentului și se confirmă prin semnătura persoanei care a întocmit/corectat documentul, menționându-se și data efectuării corecturii." — OMFP nr. 2634/2015, Anexa 1, pct. 14 (principiul general de corectare a documentelor financiar-contabile pe hârtie, adaptat digital)
:::

Principiul din normă (corectarea vizibilă, nu ștergerea tacită a urmei operațiunii) se traduce, într-o aplicație informatizată, prin păstrarea unui traseu clar al corectării — de aici cele două căi distincte de mai jos, în funcție de starea notei.

## Pașii de corectare

1. **Dacă nota generată de reconciliere e încă ciornă (nevalidată)**: o poți șterge direct din jurnal. Ștergerea readuce automat linia de extras pe starea „potrivită", disponibilă pentru realocare corectă din ecranul Bancă, la furnizorul potrivit.
2. **Dacă nota a fost deja validată**: ștergerea nu mai e permisă (doar ciornele se pot șterge). Corectarea se face prin dezlegarea legăturii dintre notă și factura greșită — o acțiune care necesită rol de administrator al firmei și un motiv obligatoriu, fără de care sistemul refuză operațiunea. Factura devine din nou „deschisă", dar linia de extras rămâne afișată drept „contată", fără buton de realocare automată — trebuie creată manual o notă nouă, corectă, din jurnalul contabil.
3. **Ambele căi sunt blocate dacă luna contabilă în care s-a înregistrat operațiunea a fost deja închisă** — corectarea trebuie făcută înainte de închiderea lunii, altfel rămâne needitabilă pe acest circuit.

## Ce se greșește în practică

- Se încearcă ștergerea unei note deja validate, fără să se știe că sistemul o refuză explicit — trebuie folosită calea de dezlegare, nu ștergerea.
- Se dezleagă nota de la factura greșită, dar nu se creează manual nota nouă corectă — furnizorul real rămâne, în continuare, cu factura neplătită în evidență.
- Se încearcă orice corectare după închiderea lunii contabile, fără să se știe că operațiunea e blocată la acel moment — corectarea reală ajunge să se facă printr-o notă de regularizare separată, în luna curentă.

## Ce face iConta.eu

iConta.eu tratează diferit o notă ciornă de una validată: pentru ciorne, ștergerea readuce automat linia bancară pe starea „potrivită", gata de realocare corectă direct din ecranul Bancă. Pentru note deja validate, aplicația cere explicit rol de administrator și un motiv, iar la dezlegare afișează clar că factura originală trebuie corectată printr-o notă nouă — dacă acțiunea nu e permisă (de exemplu luna e închisă), afișează eroarea corespunzătoare în loc să permită o corectare inconsecventă.

[iConta.eu](/)
