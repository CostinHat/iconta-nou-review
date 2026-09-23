---
title: "Decontul de perisabilitate: cum se întocmește"
description: Nota de perisabilitate cere trei date obligatorii — valoarea intrărilor, procentul de limită și pierderea constatată — plus condițiile documentare din HG 831/2004, care rămân în sarcina contabilului, nu ale aplicației.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Decontul de perisabilitate: cum se întocmește

Întocmirea notei de perisabilitate presupune trei date de intrare — valoarea intrărilor de marfă, procentul de limită aplicabil grupei și pierderea efectiv constatată — plus îndeplinirea condițiilor documentare cerute de lege. Fără aceste elemente, nota nu poate separa corect partea deductibilă de cea nedeductibilă.

## Temeiul legal

::: ghid-temei
„Se aprobă Normele privind limitele admisibile de perisabilitate la mărfuri în procesul de comercializare, prevăzute în anexa care face parte integrantă din prezenta hotărâre."

*(HG nr. 831/2004, art. 1)*
:::

## Datele de intrare

1. **Valoarea intrărilor** (`valoare_intrari`) — prețul de înregistrare al produselor intrate în perioadă, nu stocul final.
2. **Procentul de limită** (`procent_limita`) — coeficientul din anexele HG 831/2004, pe grupa de marfă corectă; se introduce manual, nu se preia automat.
3. **Pierderea constatată** (`pierdere_constatata`) — valoarea efectivă a lipsei, stabilită prin verificare faptică (inventariere, recepție sau predare de gestiune).
4. **Contul de stoc** (`cont_stoc`) — implicit 371, dar poate fi orice cont de stoc valid din planul de conturi al firmei (de exemplu 301).
5. **Degradare dovedită distrusă** (opțional) — bifat doar dacă degradarea calitativă și distrugerea efectivă sunt dovedite; dezactivează ajustarea de TVA, indiferent de mărimea depășirii.

Nota generată e scrisă în status `'ciorna'`, cu descrierea sufixată automat „ - HG 831/2004", și cere ca luna contabilă să fie deschisă.

## Condițiile documentare, în afara notei

Verificarea faptică, aprobarea administratorului și procesul-verbal sunt condiții cerute de temeiul legal, dar nu sunt validate sau impuse programatic de aplicație — nu există câmpuri sau bife pentru „aprobare administrator" ori „proces-verbal" în ecranul de introducere. Rămân documente de atașat separat, în dosarul contabil al firmei.

## Ce se greșește în practică

- Se completează procentul de limită fără verificare în anexa HG 831/2004 pentru grupa exactă de marfă.
- Se introduce valoarea intrărilor greșit, folosind stocul final în loc de valoarea produselor intrate în perioadă.
- Se presupune că aplicația validează condițiile documentare (proces-verbal, aprobare) — acestea rămân în afara motorului, de gestionat manual.

## Ce face iConta.eu

Ecranul Operațiuni speciale > „Perisabilități și scăzăminte" (`static/js/ecrane/operatiuni_ecran.js:292-299`) colectează cele cinci date de mai sus; funcția `nota_perisabilitati` (`core/uc_tenants.py:4085`) validează contul de stoc prin `cont_valid.cere_cont` (respinge un cont inexistent în planul firmei) și scrie nota ca ciornă, cu liniile calculate de motorul pur `core/perisabilitati.py`. Cota de TVA e obligatorie de introdus — dacă lipsește, motorul ridică eroare explicită, fără să folosească un procent implicit.

[iConta.eu](/)
