---
title: "Cum se raportează încetarea contractului în REVISAL"
description: "Termenul legal pentru raportarea încetării contractului individual de muncă în registrul general de evidență a salariaților și ce înregistrează efectiv iConta."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se raportează încetarea contractului în REVISAL

Încetarea unui contract individual de muncă trebuie raportată în registrul general de evidență a salariaților, azi ținut prin **REGES-ONLINE**. Temeiul e HG 295/2025, actul care a înlocuit vechea HG 905/2017 — cea de sub care circulă încă numele popular „REVISAL".

## Temeiul legal

::: ghid-temei
„datele prevăzute la art. 4 alin. (2) lit. q) [data și temeiul legal al încetării] se transmit cel târziu la data încetării contractului individual de muncă/la data luării la cunoștință a evenimentului ce a determinat [...] încetarea [...]"
— HG 295/2025, art. 5 alin. (1) lit. f) (sursă: anaf_surse/hg_295_2025_reges_online_registru_salariati.txt)
:::

Termenul e strict: data și temeiul legal al încetării contractului se transmit **cel târziu la data încetării** — sau, dacă angajatorul nu are cunoștință imediat de eveniment, la data la care ia cunoștință de el. Nerespectarea acestei obligații e sancționabilă contravențional: art. 9 alin. (3) lit. d) prevede amendă de la 5.000 la 8.000 lei pentru „netransmiterea modificărilor aduse datelor prevăzute la [...] lit. p) și q) [suspendare/încetare], în termenul prevăzut la art. 5 alin. (1) lit. e) și f)".

## Ce se greșește în practică

- Se confundă înregistrarea internă a datei de plecare a salariatului (utilă, de exemplu, pentru calculul statului de plată) cu raportarea efectivă către registru — sunt două lucruri diferite, iar a doua e cea supusă termenului legal și sancțiunii.
- Se amână transmiterea încetării „până la sfârșitul lunii" — termenul legal e „cel târziu la data încetării", nu la finalul perioadei de salarizare.
- Se presupune că orice buton etichetat „Încetare" dintr-o aplicație de salarizare trimite automat evenimentul către REGES-ONLINE.

## Ce face iConta.eu

În iConta.eu, butonul „Încetare" de pe rândul salariatului **înregistrează doar local**, în evidența internă a aplicației, data încetării — informație folosită pentru calculul corect al statului de plată din luna respectivă. Acest buton **nu declanșează nicio transmitere către REGES-ONLINE**.

Codul necesar pentru a trimite efectiv mesajul de încetare către registru există în aplicație și e testat separat, dar **nu este conectat** la niciun buton sau flux vizibil utilizatorului — este, în acest moment, cod scris dar neutilizat în producție. Singura acțiune pe care iConta o trimite azi efectiv către REGES-ONLINE este înregistrarea identității salariatului, din ecranul **Stat de plată**; raportarea încetării contractului rămâne, până la activarea acestei funcții, o obligație pe care angajatorul sau contabilul trebuie s-o îndeplinească prin alte mijloace, în termenul legal de mai sus.

Notă: HG 295/2025 a fost contestată în instanță și anulată în primă instanță de Curtea de Apel Constanța; decizia nu e definitivă, iar obligațiile descrise mai sus rămân în vigoare până la o hotărâre finală.

[iConta.eu](/)
