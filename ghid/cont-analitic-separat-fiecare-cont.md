---
title: "Cont analitic separat pentru fiecare cont bancar"
description: "Dacă legea contabilă obligă la deschiderea unui analitic distinct pentru fiecare cont bancar deținut de firmă, sau e doar o practică recomandată."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cont analitic separat pentru fiecare cont bancar

O firmă cu mai multe conturi bancare — lei, valută, la bănci diferite — se întreabă des dacă legea o obligă să țină un analitic distinct pentru fiecare, sub contul sintetic 512 "Conturi curente la bănci", sau dacă e suficient un singur cont global. Răspunsul scurt: legea nu impune o structură anume, ci lasă decizia la latitudinea entității.

## Temeiul legal

::: ghid-temei
„Conturile sintetice din planul de conturi se pot dezvolta pe conturi analitice în funcție de necesitățile impuse de anumite reglementări sau potrivit necesităților proprii ale fiecărei entități."
— OMFP nr. 1.802/2014, pct. 593 (sursă: anaf_surse/omfp_1802_2014_reglementari_consolidat.txt)
:::

- **Dezvoltarea pe analitice e o posibilitate, nu o obligație generală** — norma folosește "se pot dezvolta", nu "trebuie dezvoltate".
- **Există totuși necesități impuse de reglementări** care pot face analiticul obligatoriu în anumite situații — de exemplu evidența distinctă cerută de reglementări specifice unui domeniu de activitate.
- **În practică**, un analitic 512.01, 512.02 etc. pentru fiecare cont bancar e recomandat, pentru că simplifică reconcilierea bancară și controlul — dar absența lui nu constituie, prin ea însăși, o încălcare a normelor contabile.

## Ce se greșește în practică

- Se ține un singur cont sintetic 512 pentru mai multe conturi bancare reale, fără nicio distincție, ceea ce face imposibilă reconcilierea automată a extraselor și crește riscul de eroare la închiderea lunii.
- Se presupune greșit că legea impune analitic separat, când de fapt decizia e organizatorică, nu normativă.
- Se schimbă structura analiticelor de la o lună la alta, fără documentare, ceea ce rupe comparabilitatea soldurilor în timp.

## Ce face iConta.eu

Modulul de bancă din iConta.eu (`core/banca.py`) tratează fiecare cont bancar adăugat de utilizator ca entitate separată la nivel de aplicație, cu soldul și extrasul lui propriu, indiferent dacă structura contabilă de export folosește un analitic distinct sau un cont sintetic unic pentru toate conturile — alegerea structurii de analitice pentru cont 512 rămâne o decizie a contabilului, nu una impusă de aplicație.

[iConta.eu](/)
