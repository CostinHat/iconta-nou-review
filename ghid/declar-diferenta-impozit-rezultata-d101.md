---
title: "Cum declar diferența de impozit rezultată la D101?"
description: "Diferența de impozit rezultă din definitivarea anuală la cota de 16%, dar D101 rectificativă nu este încă disponibilă în aplicație."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum declar diferența de impozit rezultată la D101?

Diferența de impozit pe profit rezultă din definitivarea anuală (P40 × 16% = P411). Dacă însă diferența apare pentru că a fost descoperită o eroare DUPĂ depunerea D101, situația e diferită — și trebuie tratată onest.

## Temeiul legal

::: ghid-temei
"Toate flag-urile de stare din rădăcina XML (`d_rec`, `d_reg`, `d_reglem`, `d_anulare`, `d_succ`, `d_prof`, `d_alte`) sunt hardcodate «0» în `build_xml()` (`core/d101.py:418`), fără parametru de intrare care să le seteze." — dosarul de cercetare F027.
:::

Pentru definitivarea normală, impozitul rezultat este cota de 16% (CF art.17) aplicată pe profitul impozabil final (P40 → P411), după deduceri, add-back-uri și rezerva legală.

Dacă însă apare o diferență pentru că declarația inițială conținea o eroare, trebuie spus clar: **aplicația nu generează, în prezent, o D101 rectificativă din interfață**. D710 — motorul de rectificativă din iConta — acoperă explicit doar D100 (cod 121 micro / cod 103 profit trimestrial), nu D101. În plus, în sursele normative locale analizate nu a fost găsit un act (de tipul OPANAF) care să descrie explicit procedura de rectificare a D101, spre deosebire de D710/D100, unde OPANAF 649/2025 este citat direct. Structura oficială XML a D101 conține totuși flag-ul `d_rec`, ceea ce arată că formularul oficial suportă rectificativa — doar că procedura (cine, în ce termen, ce se anexează) nu e verificată la sursă în acest dosar.

## Ce se greșește în practică

Greșeala e să se aștepte ca o simplă redepunere prin aplicație, cu date corectate, să genereze automat o D101 rectificativă — flag-urile necesare nu sunt, în prezent, accesibile din interfață.

## Ce face iConta.eu

Pentru definitivarea inițială, aplicația calculează impozitul conform cotei de 16% și validărilor descrise în ghidurile dedicate. Pentru o eroare descoperită după depunere, corectarea trebuie făcută în prezent direct la ANAF sau printr-un flux din afara aplicației, aplicația neavând un parametru pentru a seta flag-urile de rectificare din structura D101.

[iConta.eu](/)
