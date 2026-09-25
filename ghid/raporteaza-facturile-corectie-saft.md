---
title: "Cum se raportează facturile de corecție în SAF-T?"
description: "Regula ANAF pentru retransmiterea Declarației informative D406 (SAF-T) atunci când s-au identificat erori: nu se admit corecții parțiale, ci doar refacerea integrală a fișierului."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se raportează facturile de corecție în SAF-T?

Instrucțiunile oficiale de depunere a Declarației informative D406 (fișierul standard de control fiscal, SAF-T) nu vorbesc separat despre „facturi de corecție" ca operațiune distinctă, ci tratează orice eroare constatată — inclusiv una legată de facturi — prin regula generală de rectificare a întregului fișier depus.

## Temeiul legal

::: ghid-temei
„6. În situaţia în care contribuabilul constată anumite erori în declaraţia depusă iniţial, acesta poate depune declaraţii rectificative. [...] 11. Pentru declaraţia informativă D406 transmisă cu erori identificate de Agenţia Naţională de Administrare Fiscală şi pentru care a fost comunicată recipisa ce le semnalează, contribuabilul retransmite integral Declaraţia informativă D406, care trebuie să cuprindă fişierul SAF-T corectat.
12. Nu este admisă transmiterea unor corecţii parţiale prin transmiterea selectivă a înregistrărilor sau câmpurilor corectate pentru Declaraţia informativă D406 anterior transmisă şi pentru care au fost primite recipise ce semnalau erori."
— OPANAF nr. 1.783/2021 (instrucțiuni SAF-T/D406) (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

Limitare onestă: sursele disponibile nu conțin o secțiune separată, cu formulare exacte, despre corectarea unei facturi individuale (de exemplu prin stornare/notă de credit) în structura SAF-T „Invoices" — regulile de mai jos sunt cea mai apropiată prevedere reală găsită, cea privind rectificarea declarației D406 în ansamblu:

- O eroare descoperită de contribuabil (inclusiv una la o factură deja raportată) se corectează prin **depunerea unei declarații rectificative** D406, nu prin editarea „la fața locului" a unei linii.
- Dacă eroarea a fost semnalată de ANAF printr-o recipisă, contribuabilul trebuie să **retransmită integral** fișierul SAF-T corectat.
- Corecțiile parțiale — trimiterea doar a înregistrărilor sau câmpurilor modificate — sunt explicit interzise de instrucțiuni.

## Ce se greșește în practică

- Se încearcă retransmiterea doar a secțiunii „Facturi" din SAF-T, presupunând că restul fișierului rămâne valabil — instrucțiunile cer fișierul integral, corectat.
- Se ignoră recipisa de eroare primită de la ANAF și se așteaptă termenul următor de raportare pentru a corecta, deși corecția e datorată imediat ce eroarea e cunoscută.
- Se confundă corectarea unei facturi în contabilitate (stornare, notă de credit) cu corectarea raportării SAF-T aferente — sunt operațiuni conexe, dar distincte, iar a doua necesită o nouă declarație D406 completă.

## Ce face iConta.eu

Verificat în cod: `core/d406.py` și `core/d406_reconciliere.py` generează Declarația D406 din datele contabile curente ale firmei la momentul rulării; aplicația nu are un flux separat, dedicat „facturilor de corecție" în SAF-T — orice modificare a unei facturi deja transmise se reflectă la următoarea generare/retransmitere integrală a D406, în linie cu regula ANAF de mai sus, dar fără un asistent specific pentru acest scenariu.

[iConta.eu](/)
