---
title: "Greșeala de a nu verifica CUI-ul clientului"
description: Un CUI neverificat înainte de facturare poate însemna o firmă inexistentă, o denumire greșită pe factură sau un statut de plătitor de TVA presupus greșit. Verificarea directă la ANAF elimină toate aceste riscuri, iar iConta.eu o face automat la emiterea facturii.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Greșeala de a nu verifica CUI-ul clientului

Facturarea „din memorie" sau după un CUI copiat dintr-un email, fără verificare la sursă, e una dintre cele mai frecvente greșeli mărunte care produc probleme mari: denumire greșită pe factură, statut de plătitor de TVA presupus incorect, sau, în cazuri rare, un CUI care pur și simplu nu (mai) există.

## Temeiul legal

::: ghid-temei
„Orice persoană sau entitate care este subiect într-un raport juridic fiscal se înregistrează fiscal primind un cod de identificare fiscală." — Legea nr. 207/2015 privind Codul de procedură fiscală, art. 82 alin. (1)
:::

Codul de identificare fiscală e mecanismul legal prin care o firmă e recunoscută ca subiect al unui raport juridic fiscal — de aceea corectitudinea lui pe o factură nu e un detaliu formal, ci elementul care leagă documentul de firma reală.

## Ce riști dacă nu verifici

- **Denumirea greșită pe factură** — dacă firma și-a schimbat numele sau CUI-ul a fost copiat greșit, factura poate ajunge să identifice altă entitate decât cea reală.
- **Statutul de plătitor de TVA presupus, nu verificat** — a factura cu sau fără TVA pe baza unei presupuneri („cred că e plătitor") în loc de o verificare la ANAF poate duce la TVA colectată greșit sau la facturi care trebuie corectate ulterior.
- **CUI inexistent sau inactiv** — o verificare la sursă arată imediat dacă firma respectivă există în evidențele ANAF și dacă are statut activ.

## Ce se greșește în practică

- Se preia CUI-ul dintr-o factură veche a aceluiași client, fără să se verifice dacă starea firmei (plătitor TVA, activ/inactiv) s-a schimbat între timp.
- Se presupune statutul de plătitor de TVA după numele firmei sau după experiența anterioară cu firme similare, în loc de o verificare punctuală.
- Se emite factura și abia ulterior, la reconciliere sau la un control, se descoperă că CUI-ul era greșit sau firma era inactivă la data facturii.

## Ce face iConta.eu

iConta.eu interoghează direct API-ul public al ANAF pentru fiecare CUI introdus, atât la adăugarea unui partener în fișa firmei, cât și, verificat explicit, la emiterea unei facturi — ecranul de emitere face o verificare a CUI-ului beneficiarului înainte de finalizare. Răspunsul de la ANAF include existența firmei, denumirea oficială, statutul de plătitor de TVA, codul CAEN și starea de inactivitate. Această verificare a statutului de plătitor TVA la momentul emiterii se face „best-effort": dacă serviciul ANAF nu răspunde sau CUI-ul nu e găsit, aplicația nu blochează emiterea facturii, ci lasă decizia finală pe seama contabilului.

[iConta.eu](/)
