---
title: "Cum se calculează zilele de concediu pentru o fracțiune de an?"
description: "Regula legală a proporționalizării concediului de odihnă când salariatul nu lucrează tot anul calendaristic — angajare sau încetare în cursul anului, normă parțială."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se calculează zilele de concediu pentru o fracțiune de an?

Un salariat angajat în cursul anului, sau al cărui contract încetează înainte de sfârșitul anului, nu are dreptul la toate cele 20 de zile de concediu (minimul legal) — ci doar la partea proporțională cu perioada efectiv lucrată. Aceeași logică se aplică și la norma parțială.

## Temeiul legal

::: ghid-temei
„Durata minima a concediului de odihnă anual este de 20 de zile lucrătoare. [...] Durata efectivă a concediului de odihnă anual se stabileşte prin contractul colectiv de muncă aplicabil, este prevăzută în contractul individual de muncă şi se acordă proporţional cu activitatea prestată într-un an calendaristic. [...] Durata concediului de odihnă anual pentru salariaţii cu contract individual de muncă cu timp parţial se acordă proporţional cu timpul efectiv lucrat."
— Legea 53/2003 (Codul muncii), art. 140 alin. (1), (2) și (4) (sursă: anaf_surse/legea_53_2003_codul_muncii.txt)
:::

Practic, legea prevede două proporționalizări diferite, care se pot combina:

- **Proporțional cu perioada din anul calendaristic** în care a existat raport de muncă — un salariat angajat pe 1 iulie are dreptul, pentru anul respectiv, la jumătate din concediul stabilit prin contract (dacă lucrează 6 din 12 luni).
- **Proporțional cu timpul efectiv lucrat**, pentru norma parțială — un salariat cu jumătate de normă are dreptul la jumătate din zilele de concediu ale unui salariat cu normă întreagă, pentru aceeași perioadă calendaristică.
- Durata efectivă de concediu (peste minimul de 20 de zile) vine din contractul colectiv sau individual de muncă — proporționalizarea se aplică asupra acelei durate contractuale, nu doar asupra minimului legal.
- Zilele de sărbătoare legală nelucrătoare nu se includ niciodată în calculul zilelor de concediu, indiferent de proporționalizare.

## Ce se greșește în practică

- Se acordă întreg numărul de zile de concediu prevăzut în contract, indiferent de câte luni a lucrat efectiv salariatul în anul respectiv.
- Se calculează proporția doar la încetarea contractului (pentru compensarea concediului neefectuat), ignorând-o la angajare, deși regula se aplică simetric.
- Se combină greșit cele două proporționalizări (perioada din an și norma parțială), aplicându-se doar una dintre ele când ambele sunt relevante.

## Ce face iConta.eu

Verificat direct în cod: iConta.eu nu are astăzi o funcție dedicată care să calculeze automat zilele de concediu de odihnă cuvenite proporțional cu perioada lucrată dintr-un an calendaristic sau cu norma parțială — nu există, în motorul de salarizare, niciun calcul care derivă zile de concediu dintr-o perioadă lucrată; zilele de concediu (de odihnă sau medical) sunt întotdeauna un parametru introdus direct de contabil, nu un rezultat calculat de aplicație. Proporționalizarea rămâne, pentru moment, un calcul făcut manual de contabil, conform formulei de mai sus.

[iConta.eu](/)
