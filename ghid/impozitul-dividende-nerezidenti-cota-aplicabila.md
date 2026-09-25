---
title: "Impozitul pe dividende pentru nerezidenți: cota aplicabilă"
description: "Cota de impozit reținut la sursă pentru dividendele plătite unui asociat nerezident, cu temeiul legal exact și limita cotei reduse din convenția de evitare a dublei impuneri."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Impozitul pe dividende pentru nerezidenți: cota aplicabilă

Dividendele plătite unui asociat nerezident nu se declară pe D205, ca cele plătite unui asociat rezident — se declară pe D207, iar cota de impozit are un temei legal separat, chiar dacă valoarea numerică a ajuns, din 2026, identică cu cea pentru rezidenți.

## Temeiul legal

::: ghid-temei
„b) 16% pentru veniturile din dividende prevăzute la art. 223 alin. (1) lit. a)"
— Codul fiscal (Legea 227/2015), art. 224 alin. (4) lit. b), modificată prin Legea nr. 141/2025, art. II pct. 41, aplicabilă dividendelor distribuite începând cu 1 ianuarie 2026 (Legea 141/2025, art. VII lit. h))
:::

Cota internă de 16% este punctul de plecare, dar nu e neapărat cea finală:

- Dacă nerezidentul este rezident al unui stat cu care România are încheiată o **convenție de evitare a dublei impuneri**, se poate aplica o cotă redusă prevăzută de acea convenție, niciodată mai mare decât cea din Codul fiscal (art. 230 alin. (1)-(2)).
- Condiția obligatorie pentru cota redusă: nerezidentul trebuie să prezinte plătitorului de venit **certificatul de rezidență fiscală** „în momentul plății venitului". Un certificat prezentat în cursul anului rămâne valabil și „în primele 60 de zile calendaristice din anul următor".
- Fără certificat prezentat la termen, se aplică automat cota internă din Titlul VI — 16%.
- Impozitul se calculează, se reține, se declară și se plătește de către **plătitorul de venituri** (firma română), conform art. 224 alin. (1).
- Obligația de declarare există și când impozitul e suportat de plătitor, nu reținut din suma plătită nerezidentului (art. 231 alin. (1^1)).

## Ce se greșește în practică

- Se declară dividendul plătit unui asociat nerezident pe D205, ca și cum ar fi un beneficiar rezident — declarația corectă e D207.
- Se aplică automat cota redusă dintr-o convenție de evitare a dublei impuneri fără să existe un certificat de rezidență fiscală valabil, prezentat la momentul plății.
- Se confundă cota pentru dividende (art. 224 alin. (4) lit. b), 16%) cu cota generală pentru „orice alte venituri" ale nerezidenților (art. 224 alin. (4) lit. d), tot 16%, dar cu alt temei) sau cu cota de 50% aplicabilă plăților către state necooperante în tranzacții artificiale (art. 224 alin. (4) lit. c)).

## Ce face iConta.eu

D207, în iConta, este o declarație **manuală**: aplicația nu are un registru de plăți către nerezidenți din care să tragă automat lista de beneficiari, iar codul de venit, actul normativ aplicabil (Cod fiscal / convenție / acord internațional) și cota de impozit se introduc de contabil, nu se calculează automat de aplicație. Nu există, așadar, riscul unei „cote hardcodate greșite" pe D207 — dar nici o verificare automată a certificatului de rezidență sau a cotei corecte din convenție.

Ce verifică efectiv aplicația: dacă în ecranul de facturare/D205 apare un beneficiar de dividende fără CNP românesc valid, acesta e tratat automat ca nerezident, iar generarea D205 pentru el este **refuzată** — mesajul îndrumă explicit spre D207. În schimb, modulul de decontări asociați (plata efectivă a dividendului, contabilizarea 455/457) nu are nicio logică specifică pentru asociatul nerezident: nu aplică reducerea din convenție și nu diferențiază cota internă de cota redusă — verificarea și aplicarea cotei corecte, la plată, rămân integral în sarcina contabilului.

[iConta.eu](/)
