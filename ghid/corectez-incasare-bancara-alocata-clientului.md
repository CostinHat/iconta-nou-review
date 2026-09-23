---
title: Cum corectez o încasare bancară alocată clientului greșit?
description: Corectarea unei alocări greșite depinde de starea notei contabile create la reconciliere — ciornă sau validată — și e blocată dacă luna contabilă e deja închisă.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o încasare bancară alocată clientului greșit?

Se poate întâmpla ca motorul de reconciliere să propună, sau ca un contabil să confirme din greșeală, alocarea unei încasări pe facturile unui client greșit — de exemplu când doi parteneri au sume apropiate în aceeași perioadă. Modul de corectare depinde de starea în care se află nota contabilă creată la contare.

## Temeiul legal

::: ghid-temei
„Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 alin. (2)
:::

::: ghid-temei
„În documentele financiar-contabile nu sunt admise ștersături, modificări sau alte asemenea procedee [...] Erorile se corectează prin tăierea cu o linie a textului sau a cifrei greșite, concomitent înscriindu-se alături textul sau cifra corectă. Corectarea se face în toate exemplarele documentului și se confirmă prin semnătura persoanei care a întocmit/corectat documentul, menționându-se și data efectuării corecturii."
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 14
:::

Principiul din normă (corectarea vizibilă, trasabilă, nu ștergerea tăcută a unei erori) e cel pe care se sprijină și mecanismul digital de corectare din aplicație, descris mai jos — chiar dacă forma tehnică (ștergere/dezlegare cu motiv, nu tăiere cu o linie pe hârtie) e diferită de cea din normă, scrisă pentru documente pe suport hârtie.

## Cum se corectează, în funcție de starea notei

1. **Dacă nota creată la „Contează" e încă ciornă** (nevalidată): se șterge nota din Jurnal. Ștergerea readuce automat linia de extras pe starea „potrivit" în ecranul Bancă, gata de realocare corectă pe clientul potrivit, din nou prin „Alege facturile".
2. **Dacă nota a fost deja validată**: ștergerea nu mai e permisă — doar notele ciornă se pot șterge. Corectarea se face prin „dezlegarea" notei de factura greșită (disponibilă doar rolului de administrator al firmei, cu motiv obligatoriu, validat de aplicație). Factura clientului greșit redevine deschisă (neîncasată), dar linia de extras rămâne afișată „Contat ✓" în ecranul Bancă, fără buton de realocare automată — o notă corectă, pe clientul potrivit, trebuie creată manual din Jurnal.
3. **Ambele operații sunt blocate dacă luna contabilă e deja închisă** — o alocare greșită descoperită după închiderea lunii nu mai poate fi corectată pe această cale în luna respectivă.

## Ce se greșește în practică

- Se încearcă ștergerea unei note deja validate, fără să se știe că trebuie folosită „dezlegarea", cu motiv obligatoriu.
- Se dezleagă nota de pe factura greșită, dar se uită crearea notei corecte pentru clientul potrivit — factura corectă rămâne, la rândul ei, neîncasată în evidențe.
- Se descoperă eroarea abia după închiderea lunii, când corectarea directă din ecranul Bancă nu mai e posibilă.

## Ce face iConta.eu

Din Jurnal, o notă în stare „ciornă" provenită din reconciliere se poate șterge, iar linia de extras revine automat pe „potrivit". O notă deja validată se corectează prin dezlegarea de factură (rol de administrator, motiv obligatoriu) — factura redevine deschisă, dar linia de extras rămâne „Contat ✓" până se creează manual o notă nouă, corectă. Ambele acțiuni sunt blocate de aplicație dacă perioada contabilă e închisă.

[iConta.eu](/)
