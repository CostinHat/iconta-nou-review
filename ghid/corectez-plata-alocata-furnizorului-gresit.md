---
title: Cum corectez o plată alocată furnizorului greșit?
description: La fel ca la o încasare greșit alocată, corectarea unei plăți alocate furnizorului greșit depinde de starea notei — ciornă sau validată — și e blocată după închiderea lunii.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum corectez o plată alocată furnizorului greșit?

Mecanismul de corectare pentru o plată alocată greșit, pe un furnizor care nu era de fapt beneficiarul, este identic cu cel pentru o încasare alocată clientului greșit — reconcilierea bancară din iConta.eu tratează încasările și plățile prin aceleași reguli de alocare și corectare, doar direcția (facturi emise vs. facturi primite) diferă.

## Temeiul legal

::: ghid-temei
„Documentele justificative care stau la baza înregistrărilor în contabilitate angajează răspunderea persoanelor care le-au întocmit, vizat și aprobat, precum și a celor care le-au înregistrat în contabilitate, după caz."
— Legea contabilității nr. 82/1991, art. 6 alin. (2)
:::

::: ghid-temei
„În documentele financiar-contabile nu sunt admise ștersături, modificări sau alte asemenea procedee [...] Erorile se corectează prin tăierea cu o linie a textului sau a cifrei greșite, concomitent înscriindu-se alături textul sau cifra corectă. Corectarea se face în toate exemplarele documentului și se confirmă prin semnătura persoanei care a întocmit/corectat documentul, menționându-se și data efectuării corecturii."
— OMFP 2634/2015, Anexa 1 „Norme generale", pct. 14
:::

## Cum se corectează, în funcție de starea notei

1. **Dacă nota creată la „Contează" e încă ciornă**: se șterge nota din Jurnal. Ștergerea readuce automat linia de extras pe starea „potrivit" în ecranul Bancă, gata de realocare pe furnizorul corect.
2. **Dacă nota a fost deja validată**: nu se mai poate șterge. Se folosește „dezlegarea" notei de factura furnizorului greșit (rol de administrator al firmei, motiv obligatoriu). Factura furnizorului greșit redevine deschisă (neplătită), dar linia de extras rămâne „Contat ✓" în ecranul Bancă — o notă nouă, pe furnizorul corect, se creează manual din Jurnal.
3. **Ambele operații sunt blocate dacă luna contabilă e deja închisă.**

## Ce se greșește în practică

- Se caută un buton de „realocare" direct pe linia de extras odată ce ea apare „Contat ✓" — nu există; pentru o notă validată, calea e dezlegarea din Jurnal, nu ecranul Bancă.
- Se dezleagă nota de pe furnizorul greșit, dar plata rămâne neînregistrată pe furnizorul corect, care apare în continuare cu factura deschisă în rapoartele de solduri.
- Se așteaptă ca motivul obligatoriu la dezlegare să fie opțional — aplicația refuză operația fără el.

## Ce face iConta.eu

Din Jurnal, o notă „ciornă" provenită din reconciliere se șterge, iar linia de extras revine automat pe „potrivit", gata de realocare. O notă deja validată se corectează prin dezlegarea de factură (rol de administrator, motiv obligatoriu) — factura furnizorului greșit redevine deschisă, dar linia de extras rămâne marcată contată până se creează manual o notă corectă. Ambele acțiuni sunt blocate dacă perioada contabilă e închisă.

[iConta.eu](/)
