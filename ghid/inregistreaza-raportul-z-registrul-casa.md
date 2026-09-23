---
title: "Cum se înregistrează raportul Z în registrul de casă?"
description: Raportul Z generează o notă contabilă (numerarul intră în 5311), dar asta nu înseamnă că apare automat și ca linie în Registrul de casă — sunt două evidențe diferite, ținute de module separate.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se înregistrează raportul Z în registrul de casă?

Un Raport Z importat sau introdus în aplicație produce o notă contabilă — numerarul din ziua respectivă ajunge în contul 5311. Dar Registrul de casă, ca document distinct (Cod 14-4-7A), e altceva: e un raport zilnic al încasărilor/plăților în numerar, ținut separat. Cele două nu sunt automat legate, iar diferența contează în practică.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți." — OMFP nr. 2634/2015 privind documentele financiar-contabile, Anexa 2 (Norme specifice), Registrul de casă, Cod 14-4-7A
:::

Norma cere completarea **zilnică** a registrului de casă, pe baza documentelor justificative — iar bonul Z tipărit este exact un asemenea document justificativ pentru încasările în numerar ale zilei.

## Ce înregistrează efectiv un Raport Z

Fie că vine din importul unui fișier AMEF (`.p7b`/XML, conform structurii II.7 din anexa OPANAF 146/2018), fie că e introdus manual, Raportul Z produce o notă contabilă pe cote reale de TVA:

- **5311 = 707** pentru suma încasărilor în numerar din raport;
- **5125 = 707** pentru încasările prin card și orice alt tip de plată din nomenclator;
- **707 = 4427** pentru TVA aferentă fiecărei cote din raport.

Diferența dintre cele două căi de introducere contează: importul din fișierul AMEF real generează o notă **ciornă**, care așteaptă verificare, în timp ce introducerea manuală (cu câmpurile Total 11% / Total 21% / Numerar / Card) generează nota direct **validată**, fără pasul suplimentar de control.

## Ce se greșește în practică

- Se presupune că, odată introdus Raportul Z, numerarul apare automat și ca linie în ecranul „Registru de casă" al aplicației — nu apare, pentru că cele două citesc surse de date diferite.
- Se sare complet peste completarea registrului de casă în zilele cu vânzări prin casa de marcat, considerând nota contabilă suficientă — norma OMFP 2634/2015 cere totuși stabilirea zilnică a soldului de casă, indiferent de sursa numerarului.
- Se introduce a doua oară, manual, aceeași sumă ca „încasare" în registrul de casă fără să se verifice dacă nota contabilă din Raportul Z a fost deja generată — riscul e nu dublarea sumei în bilanț (notele contabile rămân corecte), ci confuzia operativă asupra a ceea ce reprezintă fiecare înregistrare.

## Ce face iConta.eu

Raportul Z (import AMEF sau introducere manuală) scrie exclusiv în jurnalul contabil al firmei — nu inserează nimic în tabela pe care se bazează ecranul „Registru de casă". Acel ecran citește dintr-o evidență separată a operațiunilor de casierie, cu categorii fixe: încasare client, plată furnizor, ridicare din bancă, depunere în bancă, avans spre decontare. Nu există, în acest moment, o categorie dedicată pentru vânzările din Raportul Z/AMEF.

Practic: suma de numerar din Raportul Z ajunge corect în contul 5311 din jurnalul contabil, dar **nu apare automat ca linie în Registrul de casă**. Dacă firma ține și acest registru operativ (cerut de OMFP 2634/2015), completarea lui pentru ziua respectivă rămâne, deocamdată, o operațiune separată, făcută de contabil.

[iConta.eu](/)
