---
title: "Cum se autorizează un program de facturare să comunice cu RO e-Factura?"
description: Un program de facturare nu „se autorizează" el însuși — se înregistrează tehnic la ANAF ca aplicație, iar autorizarea efectivă o dă utilizatorul, prin certificatul lui calificat, de fiecare dată când conectează un cabinet nou.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum se autorizează un program de facturare să comunice cu RO e-Factura?

Există două niveluri de autorizare, ușor de confundat. Unul e tehnic, al programului însuși (aplicația trebuie înregistrată la ANAF ca „client" OAuth, cu un identificator propriu). Celălalt e al utilizatorului — contabilul, cu certificatul lui calificat — și se repetă pentru fiecare cabinet care vrea să folosească programul respectiv pentru SPV/e-Factura.

## Temeiul legal

::: ghid-temei
„Persoanele juridice sau alte entități fără personalitate juridică se identifică electronic cu certificate calificate." — OMFP nr. 660/2017 privind aprobarea Procedurii de comunicare prin mijloace electronice de transmitere la distanță, art. 6 alin. (1)
:::

Indiferent cât de bine e „înregistrat" un program la ANAF, comunicarea efectivă cu SPV/e-Factura tot prin certificatul calificat al utilizatorului trece — programul nu se poate identifica singur, în locul contabilului.

## Ce se întâmplă tehnic, la nivel general

1. **Înregistrarea aplicației** — dezvoltatorul programului de facturare înregistrează aplicația la ANAF, obținând un identificator tehnic propriu (folosit apoi în orice cerere de autorizare). Acesta e un pas administrativ, făcut o singură dată de furnizorul programului, nu de fiecare utilizator.
2. **Autorizarea utilizatorului** — de fiecare dată când un cabinet vrea să conecteze programul la propriul cont SPV, contabilul e trimis către pagina de autentificare ANAF, unde alege certificatul calificat (de pe stick sau din cloud) și introduce PIN-ul. Identitatea celui care autorizează vine strict din acest pas, nu din identificatorul tehnic al programului.
3. **Legătura dintre cele două** — programul primește, în urma autorizării, un acces limitat la contul respectiv (nu la ANAF în general), valabil pentru cabinetul care tocmai s-a autorizat. Acest acces trebuie reînnoit periodic, fără intervenția utilizatorului, atâta timp cât conexiunea rămâne activă.

Notă onestă: parametrii tehnici exacți ai acestui mecanism (durata de valabilitate a accesului, limitele de frecvență a cererilor etc.) sunt documentați și verificați intern de echipa iConta la sursa ANAF, dar nu provin dintr-un act normativ — sunt proceduri tehnice ANAF, nu reglementare legală, și nu trebuie citate ca „lege".

## Ce se greșește în practică

- Se crede că „autorizarea programului" e un pas unic, valabil pentru toți clienții acelui program — de fapt, fiecare cabinet trebuie să autorizeze separat, cu propriul certificat.
- Se confundă identificatorul tehnic al aplicației (obținut o dată, de furnizor) cu identitatea celui care folosește efectiv aplicația — cel din urmă e mereu certificatul utilizatorului, nu al programului.
- Se așteaptă ca autorizarea să fie permanentă, fără nicio reînnoire — accesul acordat unui program are o valabilitate limitată în timp și trebuie reînnoit periodic, automat, cât timp conexiunea e activă.

## Ce face iConta.eu

iConta.eu este înregistrată tehnic la ANAF ca aplicație, cu propriul identificator. Pentru fiecare cabinet care vrea să folosească SPV/e-Factura prin iConta.eu, contabilul e trimis către pagina de autentificare ANAF, unde alege certificatul calificat propriu. După autorizare, accesul e păstrat criptat și reînnoit automat, fără intervenție manuală, cât timp conexiunea rămâne validă. Rezervă: mecanismul e verificat cap-coadă în producție, dar cu certificatul administratorului platformei, care nu are drept SPV pe firme reale — fluxul complet, cu un cabinet real, pe un CIF cu drept efectiv, rămâne de confirmat cazuistic.

[iConta.eu](/)
