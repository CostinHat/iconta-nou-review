---
title: "Cum înregistrezi numerarul retras din bancă pentru casierie"
description: "Ce document stă la baza ridicării de numerar din contul bancar propriu al firmei pentru alimentarea casieriei și cum se înregistrează în registrul de casă."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum înregistrezi numerarul retras din bancă pentru casierie

Ridicarea de numerar din contul bancar al firmei, pentru alimentarea propriei case de marcat sau casierii, nu e o "încasare" sau o "plată" către un terț — e o mișcare de fonduri între propriile evidențe ale aceleiași entități. De aceea nu intră sub plafoanele Legii nr. 70/2015 pentru operațiuni cu numerar (acelea reglementează relații între entități distincte), dar trebuie oricum documentată corect în registrul de casă.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți."
— OMFP nr. 2.634/2015, Anexa 2 — Norme specifice de întocmire și utilizare a documentelor financiar-contabile (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

- **Ridicarea de numerar din bancă pentru casierie proprie nu cade sub plafoanele Legii nr. 70/2015** — acele plafoane (5.000 lei/10.000 lei) privesc încasări și plăți între persoane distincte, definite la art. 1 alin. (1) din acea lege, nu transferul de fonduri în interiorul aceleiași firme.
- **Operațiunea rămâne totuși o mișcare de numerar** care trebuie consemnată zilnic în registrul de casă, pe baza documentului justificativ corespunzător — de regulă chitanța sau foaia de vărsământ emisă de bancă la ridicarea sumei.
- **Soldul de casă rezultat** intră apoi în calculul zilnic al registrului de casă, alături de toate celelalte încasări și plăți în numerar ale zilei.

## Ce se greșește în practică

- Se aplică din reflex plafonul de 5.000 lei/zi (specific plăților către furnizori) și la ridicarea de numerar din contul propriu, deși legea nu leagă cele două situații.
- Se înregistrează suma direct în casă, fără documentul justificativ de la bancă atașat, ceea ce lasă operațiunea nedemonstrată la o eventuală verificare.
- Se omite consemnarea zilnică în registrul de casă, lăsând operațiunea "în așteptare" până la sfârșitul lunii, contrar cerinței de întocmire zilnică.

## Ce face iConta.eu

Modulele de bancă și casierie din iConta.eu (`core/banca.py`, `core/casa.py`, `core/casa_api.py`) permit înregistrarea unui transfer între contul bancar și casierie ca operațiune internă, dar generarea automată a documentului justificativ (chitanța/foaia de vărsământ de la bancă) și corelarea ei cu extrasul bancar real rămân în sarcina contabilului, pe baza documentului primit efectiv de la bancă.

[iConta.eu](/)
