---
title: "Raportul Z zilnic: cum se înregistrează în registrul de casă"
description: Raportul Z generează notă contabilă (5311=707), dar asta nu e același lucru cu o linie în Registrul de casă (Cod 14-4-7A) — sunt două evidențe diferite, care nu se alimentează automat una din alta.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Raportul Z zilnic: cum se înregistrează în registrul de casă

Aici e o confuzie frecventă, pentru că sună ca același lucru: „Raportul Z intră în registrul de casă" nu înseamnă că apare ca rând în evidența operativă de casă. Sunt două documente diferite, cu roluri diferite.

## Temeiul legal

::: ghid-temei
„Registrul de casă servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității; - document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți." — OMFP 2634/2015, Anexa 2 (Norme specifice), Registrul de casă (Cod 14-4-7A)
:::

## Ce înseamnă practic

Raportul Z generat prin funcționalitatea „Raport Z" (import AMEF sau introducere manuală) produce o **notă contabilă** — jurnalul dublei intrări, cu `5311 = 707` pentru partea de numerar, `5125 = 707` pentru card, `707 = 4427` pentru TVA colectată. Asta e evidența de rezultat (venituri, TVA), ținută în registrul jurnal.

**Registrul de casă**, în sensul OMFP 2634/2015, e o evidență separată — operativă, zi de zi, a mișcărilor de numerar prin casierie, cu sold rulant. Suma de numerar din Raportul Z ajunge, prin nota contabilă, în soldul contului 5311 din balanță — dar nu apare ca rând distinct în ecranul/raportul „Registru de casă" al aplicației, pentru că acel raport citește exclusiv operațiunile de casierie introduse separat (încasare client, plată furnizor, ridicare/depunere bancă, avans spre decontare), nu notele generate de Raportul Z.

## Ce se greșește în practică

Presupunerea că soldul din „Registru de casă" reflectă și numerarul din vânzările HoReCa înregistrate prin Raport Z. Dacă firma ține și registrul de casă operativ (obligatoriu conform OMFP 2634/2015, întocmit zilnic), încasarea de numerar din ziua respectivă trebuie introdusă **separat**, ca operațiune de casierie — altfel soldul de casă din registrul operativ nu se potrivește cu numerarul contabilizat prin 5311.

## Ce face iConta.eu

Cele două module sunt distincte în aplicație: Raportul Z scrie note contabile direct în jurnal (sursă `amef` sau `horeca_z`), în timp ce Registrul de casă citește o tabelă proprie de operațiuni de casierie, cu categorii fixe (încasare client, plată furnizor, ridicare/depunere bancă, avans spre decontare). Raportul Z **nu** alimentează automat această a doua tabelă — dacă ai nevoie de un registru de casă operativ complet pe zi, încasarea de numerar din Z trebuie adăugată și acolo, ca operațiune separată.

[iConta.eu](/)
