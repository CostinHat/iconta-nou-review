---
title: "Cum se închide tura la casierie 2026"
description: "Ce rol are, potrivit reglementărilor contabile OMFP 2634/2015, Registrul de casă în stabilirea soldului zilnic al casieriei și cum se documentează închiderea zilei/turei."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se închide tura la casierie 2026

„Închiderea turei" nu e un concept contabil separat — documentul care face, de fapt, această închidere e Registrul de casă, iar reglementările contabile îi stabilesc explicit rolul de a fixa soldul de casă la sfârșitul fiecărei zile.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP 2634/2015, Anexa 2, cod 14-4-7/a (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Ce reiese, strict din text, pentru procedura de „închidere":

- Registrul de casă se întocmește **zilnic**, nu pe ture — reglementarea nu recunoaște conceptul de „tură" ca unitate contabilă separată, ci ziua calendaristică, pe baza documentelor justificative de încasări și plăți acumulate.
- Rolul lui explicit e să **stabilească soldul de casă la sfârșitul fiecărei zile** — acesta e, practic, echivalentul contabil al „închiderii" pe care o cere o firmă cu program pe ture: la finalul zilei (nu al fiecărei ture individuale), se totalizează încasările și plățile și se determină soldul rămas în numerar.
- Dacă firma lucrează cu mai multe ture în aceeași zi, reglementarea nu impune un registru de casă separat per tură — obligația legală e un singur sold zilnic, documentat prin Registrul de casă, indiferent de câte ture s-au succedat.
- Pentru firmele care operează cu case de marcat electronice fiscale, procedura de raport Z (închiderea zilnică a aparatului de marcat) e un proces complementar, reglementat separat, care nu se regăsește în textul citat aici.

## Ce se greșește în practică

- Se întocmește un Registru de casă separat pentru fiecare tură, tratând-o ca unitate contabilă de sine stătătoare — reglementarea cere un sold stabilit la sfârșitul fiecărei **zile**, nu al fiecărei ture.
- Se omite completarea Registrului de casă în ziua respectivă, amânând-o pentru mai târziu — documentul „se întocmește zilnic", pe baza documentelor justificative acumulate în acea zi, nu retroactiv, la o dată ulterioară.
- Se confundă închiderea Registrului de casă cu raportul Z al casei de marcat electronice fiscale — sunt documente diferite, cu roluri complementare, nu interschimbabile.

## Ce face iConta.eu

Modulul de casierie al iConta.eu (`core/casa.py`) calculează automat soldul de casă zilnic pe baza operațiunilor introduse (`registru_casa`, `sold_final`) și verifică încadrarea în plafoanele legale de numerar (`verifica_plafon`). Această funcționalitate reflectă direct cerința legală de stabilire a soldului de casă la sfârșitul fiecărei zile. La data acestui ghid, iConta.eu **nu gestionează explicit conceptul de „tură"** ca subdiviziune a zilei de casierie — soldul se calculează și se închide la nivel de zi, nu la nivel de tură individuală, iar structurarea internă pe ture (dacă firma o folosește operațional) rămâne în afara evidenței aplicației.

[iConta.eu](/)
