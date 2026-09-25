---
title: "Eroarea de a alege un CAEN greșit la înființare: cum o corectez"
description: "Cum se corectează un cod CAEN ales greșit la înființarea firmei, plecând de la faptul că obiectul de activitate este element obligatoriu al actului constitutiv."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Eroarea de a alege un CAEN greșit la înființare: cum o corectez

Codul CAEN nu este un detaliu administrativ oarecare — obiectul de activitate al firmei, cu precizarea domeniului și a activității principale, este un element pe care legea îl impune expres în actul constitutiv al societății. O eroare la acest capitol nu se remediază printr-o simplă notificare, ci printr-o **modificare a actului constitutiv**, cu mențiunea corespunzătoare la Registrul Comerțului.

## Temeiul legal

::: ghid-temei
„Actul constitutiv al societății în nume colectiv, în comandită simplă sau cu răspundere limitată va cuprinde: [...] c) obiectul de activitate al societății, cu precizarea domeniului și a activității principale;"
— Legea nr. 31/1990 a societăților, art. 7 lit. c) (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

- Obiectul de activitate (deci și codul CAEN al activității principale) este un element **obligatoriu** al actului constitutiv, alături de datele asociaților, forma și denumirea societății, capitalul social și sediul social.
- Corectarea unui CAEN greșit ales la înființare presupune, ca regulă, o **modificare a actului constitutiv** — de regulă printr-o hotărâre a asociaților/acționarilor — urmată de înregistrarea mențiunii corespunzătoare la Oficiul Registrului Comerțului.
- Codul CAEN al activității principale nu este doar o formalitate: are consecințe fiscale reale — de exemplu, Codul fiscal condiționează explicit anumite regimuri (precum eligibilitatea sau ieșirea din impozitul micro pentru firmele din HoReCa) de codurile CAEN înregistrate ca activitate principală sau secundară.
- Până la corectarea CAEN-ului, firma funcționează oficial cu obiectul de activitate greșit înregistrat, ceea ce poate ridica probleme la autorizarea unor activități specifice sau la interpretarea unor obligații fiscale legate de domeniul de activitate.

## Ce se greșește în practică

- Se presupune că un CAEN greșit se poate corecta printr-o simplă cerere sau adresă la ANAF, fără a trece prin modificarea actului constitutiv la Registrul Comerțului.
- Se confundă activitatea principală (care determină, printre altele, anumite obligații fiscale specifice unor domenii) cu activitățile secundare, alegându-se greșit care cod CAEN e declarat ca principal.
- Se amână corectarea unui CAEN greșit, considerând-o o problemă minoră, deși unele regimuri fiscale (de exemplu regulile speciale pentru micro din HoReCa) sunt condiționate explicit de codurile CAEN înregistrate.
- Nu se verifică, la corectare, dacă noul cod CAEN ales necesită autorizații sau avize suplimentare specifice domeniului de activitate.

## Ce face iConta.eu

Din verificarea codului sursă, iConta.eu **validează formatul** codului CAEN introdus în profilul firmei — de exemplu, la generarea declarației D101, aplicația verifică dacă CAEN-ul are exact 4 cifre și semnalează eroarea „cod CAEN invalid... Corectează în Profil firmă" dacă nu respectă acest format; similar, la D112 există o verificare dacă CAEN-ul se regăsește în nomenclatorul oficial acceptat de declarație. Aceste verificări țin însă de validarea datelor pentru declarațiile fiscale generate în aplicație, nu de procedura de **corectare a CAEN-ului greșit la Registrul Comerțului** — acest demers, descris mai sus, rămâne unul realizat direct la ONRC, în afara iConta.eu.

[iConta.eu](/)
