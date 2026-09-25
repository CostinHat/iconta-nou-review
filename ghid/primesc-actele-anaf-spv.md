---
title: "Cum primesc actele de la ANAF prin SPV"
description: "Cum se comunică legal actele administrative fiscale prin Spațiul Privat Virtual și de la ce dată se consideră primite, conform Codului de procedură fiscală."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum primesc actele de la ANAF prin SPV

Comunicarea electronică a actelor fiscale nu e doar o comoditate — are efecte juridice precise: din momentul în care actul e pus la dispoziție prin mijloace electronice, curg termenele de contestare sau de conformare, exact ca și cum actul ar fi fost primit prin poștă.

## Temeiul legal

::: ghid-temei
„(15) Actul administrativ fiscal emis în formă electronică se comunică prin mijloace electronice de transmitere la distanță potrivit alin. (16) sau (17), după caz, iar acesta se consideră comunicat la data punerii la dispoziția contribuabilului/plătitorului prin aceste mijloace.
(16) în cazul actelor administrative fiscale emise de către organul fiscal central, mijloacele electronice de transmitere la distanță, procedura de comunicare a actelor administrative fiscale prin mijloace electronice de transmitere la distanță, precum și condițiile în care aceasta se realizează se aprobă prin ordin al președintelui A.N.A.F., cu avizul Autorității pentru Digitalizarea României."
— Legea 207/2015, art. 47 alin. (15)-(16) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

Ce înseamnă practic pentru un contribuabil înregistrat în SPV:

- Actele emise de ANAF în formă electronică (decizii de impunere, notificări, somații etc.) se consideră **comunicate la data la care sunt puse la dispoziție** în Spațiul Privat Virtual — nu la data la care contribuabilul le deschide sau le citește efectiv.
- Din acea dată curg termenele legale (de exemplu cele 45 de zile pentru contestație, prevăzute la art. 270), deci verificarea periodică a SPV nu e opțională odată ce firma e înregistrată acolo.
- Legea prevede și o situație specifică: contribuabilii înregistrați din oficiu de ANAF în sistemul electronic, care nu accesează sistemul în 15 zile de la comunicarea datelor de înregistrare, primesc actele respective doar prin publicitate (afișare), nu individual — un motiv în plus pentru a verifica activ SPV.

## Ce se greșește în practică

- Se consideră că un act "nu a fost primit" dacă nu a fost deschis sau citit — legal, data comunicării e data punerii la dispoziție în sistem, indiferent de data accesării efective.
- Se verifică SPV ocazional sau doar când se așteaptă ceva anume, ceea ce poate duce la pierderea termenului de contestație pentru un act comunicat electronic fără ca firma să fi observat.
- Se confundă comunicarea actelor administrative fiscale (reglementată la art. 47) cu primirea facturilor prin RO e-Factura — sunt fluxuri și reguli diferite, deși ambele trec prin SPV.

## Ce face iConta.eu

iConta.eu se conectează la ANAF prin conectorul SPV propriu (OAuth2, cu token criptat) și descarcă automat, pe fir dedicat, mesajele și facturile primite prin acest canal — dar la data acestui ghid, descărcarea automată acoperă în principal fluxul de e-Factura (facturi primite de la furnizori), nu comunicarea generală a actelor administrative fiscale de la art. 47. Pentru decizii de impunere, notificări sau alte acte administrative, contabilul trebuie să verifice separat contul SPV al firmei.

[iConta.eu](/)
