---
title: "Cum se justifică sumele ridicate din casierie"
description: "Documentele justificative pentru avansuri și retrageri de numerar din casierie — ordinul de deplasare și dispoziția de plată."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum se justifică sumele ridicate din casierie

O sumă ridicată din casierie fără document justificativ corespunzător nu poate rămâne validă în contabilitate. Normele metodologice ale documentelor financiar-contabile stabilesc exact ce formular acoperă fiecare tip de retragere, în funcție de scopul ei.

## Temeiul legal

::: ghid-temei
„Ordinul de deplasare (delegație) se întocmește pentru fiecare deplasare, de către persoana care urmează a efectua deplasarea, precum și pentru justificarea avansurilor acordate în vederea procurării de valori materiale cu plata în numerar. În cazul în care la decontarea avansului suma cheltuielilor efectuate este mai mare decât avansul primit, pentru diferența de primit de către titularul de avans se întocmește Dispoziție de plată către casierie (cod 14-4-4)."
— OMFP 2634/2015, Anexa 2 (sursă: anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt)
:::

Documentele corecte, în funcție de situație:

- **Avans pentru procurare de bunuri cu plata în numerar** — se justifică prin ordinul de deplasare (delegație, cod 14-5-4), chiar dacă nu e vorba de o deplasare propriu-zisă, ci de o achiziție cu numerar.
- **Diferența de primit de titularul avansului** (cheltuit mai mult decât avansul primit) — se emite Dispoziție de plată către casierie (cod 14-4-4).
- **Diferența de restituit de titularul avansului** (cheltuit mai puțin decât avansul primit) — se depune la casierie pe bază de Dispoziție de încasare către casierie (cod 14-4-4).
- **Deplasările în străinătate** — se decontează prin Decontul de cheltuieli pentru deplasări externe (cod 14-5-5), care servește simultan ca document de decontare și ca document justificativ de înregistrare în Registrul de casă (în valută) și în contabilitate. Doar pentru transporturile internaționale (conducători auto) se folosește varianta specială, Decontul de cheltuieli valutare (cod 14-5-5/a).

## Ce se greșește în practică

- Se ridică numerar din casierie „pentru cheltuieli", fără emiterea documentului corespunzător (ordin de deplasare sau dispoziție de plată), lăsând operațiunea nejustificată până la o decontare ulterioară incompletă.
- Se decontează avansul fără a distinge diferența de primit de diferența de restituit — cele două se justifică prin documente diferite (dispoziție de plată, respectiv dispoziție de încasare).
- Se tratează la fel un avans pentru deplasare și un avans pentru achiziție de bunuri, deși ambele folosesc ordinul de deplasare — dar cu conținut și justificare diferite, care trebuie reflectate corect în descrierea operațiunii.

## Ce face iConta.eu

iConta.eu are un registru de casă (`core/casa_api.py`) în care fiecare operațiune se introduce cu categorie, sumă, document justificativ și, unde e cazul, partener — aplicația generează automat nota contabilă asociată (ca ciornă, validată apoi de contabil) și avertizează la depășirea plafoanelor legale de casă. Aplicația nu generează însă formularele tipizate propriu-zise (Ordin de deplasare cod 14-5-4, Dispoziție de plată/încasare către casierie cod 14-4-4) — acestea rămân documente separate, pe care contabilul le întocmește și le atașează operațiunii înregistrate.

[iConta.eu](/)
