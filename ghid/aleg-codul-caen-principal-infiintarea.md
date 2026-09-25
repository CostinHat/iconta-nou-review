---
title: "Cum aleg codul CAEN principal la înființarea unui SRL"
description: "Ce reglementează, de fapt, Legea societăților despre obiectul de activitate al firmei și unde se stabilește efectiv codul CAEN principal."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum aleg codul CAEN principal la înființarea unui SRL

Alegerea codului CAEN principal e una dintre primele decizii formale la înființarea unei firme — de el depind, printre altele, unele obligații de autorizare și încadrări fiscale specifice unor domenii. Merită clarificat ce anume reglementează legea societăților și unde se află, de fapt, regulile tehnice de clasificare.

## Temeiul legal

::: ghid-temei
„Asociații nu pot lua parte, ca asociați cu răspundere nelimitată, în alte societăți concurente sau având același obiect de activitate, nici să facă operațiuni în contul lor sau al altora, în același fel de comerț sau într-unul asemănător, fără consimțământul celorlalți asociați."
— Legea nr. 31/1990 (Legea societăților), art. 82 (sursă: anaf_surse/legea_31_1990_societatile.txt)
:::

**Limitare declarată:** textul de mai sus arată că Legea societăților nr. 31/1990 vorbește despre „obiectul de activitate" al firmei — folosit ca noțiune juridică (de exemplu pentru interdicția de concurență a asociaților cu răspundere nelimitată) — dar **nu conține reguli tehnice despre alegerea codului CAEN principal**. Clasificarea CAEN (Clasificarea Activităților din Economia Națională) e un sistem de nomenclatură statistică, stabilit prin acte ale Institutului Național de Statistică, nu prin Legea societăților sau prin Codul fiscal, iar aceste acte nu se regăsesc în sursele verificate pentru acest ghid. Ce se poate spune cu certitudine, din practica de înregistrare la Registrul Comerțului:

- Codul CAEN principal declarat la înființare trebuie să corespundă activității economice efective, principale, pe care firma urmează să o desfășoare.
- Anumite coduri CAEN atrag obligații suplimentare de autorizare (avize, licențe) înainte de începerea efectivă a activității, în funcție de domeniu — acestea sunt reglementate sectorial, nu de Legea societăților.
- Codul CAEN principal poate fi schimbat ulterior, prin mențiune la Registrul Comerțului, dacă activitatea reală a firmei se schimbă.

## Ce se greșește în practică

- Se caută în Legea societăților sau în Codul fiscal o listă de reguli pentru alegerea CAEN — clasificarea propriu-zisă e un nomenclator statistic, administrat separat, nu o reglementare fiscală sau comercială directă.
- Se alege un cod CAEN „generic" fără legătură cu activitatea reală planificată, ceea ce poate crea probleme ulterioare la obținerea de autorizații specifice domeniului real de activitate.
- Se ignoră faptul că anumite coduri CAEN implică obligații de autorizare prealabilă — firma nu poate începe efectiv activitatea doar pe baza înregistrării la Registrul Comerțului, dacă domeniul respectiv cere avize suplimentare.

## Ce face iConta.eu

Verificat în cod: iConta.eu preia codul CAEN al firmei direct din registrul public al ANAF, prin integrarea cu API-ul de date de identificare (câmpul `cod_caen`, citit din răspunsul oficial al agenției) — aplicația **afișează** codul CAEN existent al firmei, dar nu oferă o funcționalitate de recomandare sau validare a alegerii codului CAEN la înființare. Decizia asupra codului CAEN principal se ia înainte de înregistrarea firmei la Registrul Comerțului, în afara aplicației.

[iConta.eu](/)
