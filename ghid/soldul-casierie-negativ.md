---
title: "Ce fac dacă soldul din casierie este negativ?"
description: "De ce un sold negativ în registrul de casă e semnul unei erori de înregistrare, conform structurii Registrului de casă din OMFP 2634/2015, și cum se corectează."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Ce fac dacă soldul din casierie este negativ?

Numerarul existent fizic într-o casierie nu poate fi, prin definiție, o cantitate negativă — dacă registrul de casă arată un sold negativ, problema nu e casieria, ci o înregistrare lipsă sau greșită în evidența contabilă.

## Temeiul legal

::: ghid-temei
Modelul oficial al Registrului de casă (cod 14-4-7A) structurează fiecare zi ca: „Report/Sold ziua precedentă", urmat de coloanele „Încasări" și „Plăți", cu totalul de reportat pe pagina următoare.
— OMFP 2634/2015, Anexa 3 — modelul Registrului de casă, cod 14-4-7A (sursă: anaf_surse/omfp_2634_2015_anexa3_modele.txt)
:::

Din chiar structura registrului rezultă mecanismul erorii:

- soldul zilei se calculează **exclusiv aritmetic**: sold precedent + încasări − plăți — dacă rezultatul e negativ, înseamnă că au fost înregistrate plăți mai mari decât numerarul efectiv disponibil, ceea ce e imposibil fizic (nu poți plăti cash mai mult decât ai în sertar);
- cauza tipică e o **încasare neînregistrată sau înregistrată cu întârziere** (o factură încasată cash, dar introdusă în sistem după ce s-au efectuat plățile aferente) sau o **plată dublată/greșit datată**;
- corectarea urmează regulile generale de corectare a erorilor contabile (OMFP 1802/2014, pct. 65-69): dacă eroarea aparține perioadei curente, se corectează direct, prin identificarea și înregistrarea documentului lipsă la data lui reală; dacă aparține unui exercițiu financiar deja închis și e semnificativă, corectarea trece prin contul 1174 „Rezultatul reportat provenit din corectarea erorilor contabile";
- până la identificarea cauzei, soldul negativ e un semnal de **eroare de evidență**, nu o stare contabilă validă care poate fi „acceptată" sau reportată mai departe.

## Ce se greșește în practică

- Se acceptă soldul negativ ca fiind „temporar" și se continuă înregistrarea operațiunilor următoare, fără să se caute documentul lipsă — eroarea se propagă și devine tot mai greu de localizat cu fiecare zi care trece.
- Se corectează soldul prin înregistrarea unei „încasări fictive" doar pentru a echilibra registrul, fără document justificativ real — asta creează o discrepanță în plus între contabilitate și realitatea faptică a casieriei, verificabilă la un control.
- Se confundă un sold de casă negativ cu un simplu decalaj de raportare (de exemplu, o depunere la bancă înregistrată cu o zi înainte de a fi efectiv făcută) — cele două situații cer verificări diferite: una ține de documente lipsă, cealaltă de datare greșită.

## Ce face iConta.eu

iConta.eu gestionează casieria și avansurile de trezorerie printr-un modul dedicat (`core/casa.py`), cu plafoanele de încasări/plăți în numerar aplicabile (Legea 70/2015) și monografiile contabile din OMFP 1802/2014. La data acestui ghid, aplicația nu are o verificare automată explicită care să blocheze sau să semnaleze special un sold de casă negativ rezultat din operațiuni introduse — identificarea cauzei rămâne un pas de verificare manuală, pe baza reconcilierii dintre operațiunile înregistrate și documentele justificative reale.

[iConta.eu](/)
