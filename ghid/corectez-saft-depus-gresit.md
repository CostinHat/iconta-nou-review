---
title: "Cum corectez un SAF-T depus greșit"
description: "D406/SAF-T nu se corectează parțial: procedura legală cere retransmiterea integrală a fișierului corectat, iar iConta.eu tratează redepunerea prin fluxul generic al oricărei declarații."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectez un SAF-T depus greșit

Dacă ai depus deja o Declarație informativă D406 (SAF-T) și constați ulterior o eroare — a ta sau semnalată de ANAF — procedura de corecție e clară și restrictivă în același timp: se depune o rectificativă, dar aceasta trebuie să conțină fișierul SAF-T **întreg**, refăcut corect, nu doar partea greșită.

## Temeiul legal

::: ghid-temei
„6. În situaţia în care contribuabilul constată anumite erori în declaraţia depusă iniţial, acesta poate depune declaraţii rectificative.
[...]
11. Pentru declaraţia informativă D406 transmisă cu erori identificate de Agenţia Naţională de Administrare Fiscală şi pentru care a fost comunicată recipisa ce le semnalează, contribuabilul retransmite integral Declaraţia informativă D406, care trebuie să cuprindă fişierul SAF-T corectat.
12. Nu este admisă transmiterea unor corecţii parţiale prin transmiterea selectivă a înregistrărilor sau câmpurilor corectate pentru Declaraţia informativă D406 anterior transmisă şi pentru care au fost primite recipise ce semnalau erori."
— OPANAF 1783/2021, Anexa 4, pct. 6, 11, 12 (sursă: anaf_surse/opanaf_1783_2021_saft_d406.txt)
:::

- Pasul 1, indiferent de sursa erorii: identifică exact ce e greșit în datele care au generat fișierul SAF-T (planul de conturi mapat greșit, facturi omise, solduri incorecte) — corecția se face la sursa datelor, nu direct în XML.
- Pasul 2: regenerezi fișierul SAF-T complet, cu corecția inclusă, pentru toate secțiunile relevante ale perioadei respective — nu doar cele afectate de eroare.
- Pasul 3: retransmiți fișierul ca declarație rectificativă. Dacă eroarea a fost semnalată de ANAF printr-o recipisă, retransmiterea integrală e **obligatorie** (pct. 11), nu la alegere.

## Ce se greșește în practică

- Se încearcă trimiterea doar a secțiunii corectate (de exemplu doar lista de facturi greșit mapate) — interzis explicit la pct. 12; SAF-T-ul corectat trebuie să fie complet.
- Se corectează eroarea în datele contabile, dar se uită regenerarea și redepunerea efectivă a fișierului SAF-T — corecția rămâne „doar în evidența internă", fără să ajungă la ANAF.
- Se așteaptă o notificare oficială înainte de a corecta o eroare pe care contribuabilul a găsit-o singur — pct. 6 permite corectarea din proprie inițiativă, fără să fie nevoie de o recipisă de eroare de la ANAF.

## Ce face iConta.eu

Codul aplicației nu tratează D406 ca un caz special de „corecție" — nu există niciun concept dedicat de rectificativă SAF-T în modulul care generează D406. O redepunere a unui D406 corectat pentru aceeași perioadă parcurge exact fluxul generic al oricărei declarații din iConta.eu: se regenerează declarația din ecranul de Declarații, intră în coada de aprobare (control „patru ochi"), și se depune din nou — indiferent dacă tipul e D406, D300 sau altul.

La nivelul bazei de date, fiecare depunere nouă pentru aceeași perioadă primește un număr de versiune propriu și e păstrată separat de depunerea anterioară, fără suprascriere — deci istoricul depunerilor (inclusiv cea greșită și cea corectată) rămâne disponibil pentru motoarele interne de control. Ce nu face aplicația: nu validează automat dacă fișierul SAF-T retransmis e într-adevăr complet, conform regulii de la pct. 11-12 — respectarea acestei reguli rămâne responsabilitatea contabilului la momentul generării declarației.

[iConta.eu](/)
