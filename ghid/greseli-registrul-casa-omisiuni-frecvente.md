---
title: "Greșeli la registrul de casă: omisiuni frecvente"
description: "Cele mai frecvente omisiuni la completarea registrului de casă și regulile de plafon numerar care le fac vizibile, potrivit Legii 70/2015 și OMFP 2634/2015."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Greșeli la registrul de casă: omisiuni frecvente

Registrul de casă e documentul care înregistrează, zilnic, toate încasările și plățile în numerar prin casieria firmei. Fiind un document operativ, completat manual sau semi-automat în majoritatea firmelor mici, e locul unde apar cel mai des omisiuni — unele fără consecințe, altele care duc direct la depășirea plafoanelor legale de numerar.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP 2634/2015, Norme specifice privind formularele financiar-contabile (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Cele mai frecvente omisiuni:

- **Nu se completează zilnic** — se scriu mai multe zile deodată, retroactiv, ceea ce face soldul de casă zilnic (obligatoriu, potrivit definiției de mai sus) practic nesigur pentru zilele intermediare.
- **Lipsesc documentele justificative** pentru operațiuni individuale — dispoziția de plată/încasare către casierie e documentul de bază pentru orice plată sau încasare fără altă factură/chitanță atașată; fără ea, operațiunea nu are cum fi justificată la un control.
- **Nu se verifică plafoanele de numerar** la fiecare operațiune — Legea 70/2015 (actualizată prin Legea 239/2025) stabilește plafoane pentru plăți și încasări în numerar către/de la persoane juridice, iar depășirea lor e sancționabilă, indiferent dacă registrul e completat corect din punct de vedere formal.
- **Se omit avansurile de trezorerie nedecontate** din reclasificarea de bilanț la finalul exercițiului — un avans acordat unui angajat și nedecontat la timp rămâne o sumă „în aer" în evidența de casă dacă nu e urmărit separat.
- **Soldul de casă nu se recalculează după corectarea unei erori** dintr-o zi anterioară — o corecție introdusă azi trebuie să propage soldul corect prin toate zilele ulterioare, nu doar în ziua corectării.

## Ce se greșește în practică

- Se completează registrul de casă din memorie, la finalul lunii, pe baza bonurilor adunate, ceea ce face imposibilă stabilirea soldului zilnic real, cerut explicit de norme.
- Se tratează plafonul de numerar ca o limită „pe operațiune izolată", fără cumularea plăților către același partener în aceeași zi, deși legea urmărește tocmai evitarea fragmentării artificiale a plăților.
- Nu se ține o evidență separată, clară, a avansurilor de trezorerie acordate și nedecontate, ceea ce le face greu de distins de o simplă ieșire de numerar fără justificare.

## Ce face iConta.eu

Modulul de casierie din iConta.eu (`core/casa.py`, `core/casa_api.py`) generează registrul de casă pe baza operațiunilor introduse, calculează soldul final zi de zi și verifică automat încadrarea în plafoanele legale de numerar (`verifica_plafon`), cu sursele actualizate — Legea 70/2015, în vigoare cu modificările din Legea 239/2025 (plafon 01.01.2026) și OMFP 1802/2014 pentru monografiile contabile. Aplicația ține și evidența avansurilor de trezorerie (acordare, restituire, decontare, reclasificare la bilanț). La data acestui ghid, iConta.eu **nu poate detecta o operațiune introdusă cu întârziere față de data reală** (de exemplu, o zi completată retroactiv) — corectitudinea cronologică a introducerii datelor rămâne responsabilitatea celui care operează în cont.

[iConta.eu](/)
