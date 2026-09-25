---
title: "Cum pregătesc un magazin online pentru e-TVA 2026"
description: "Obligațiile persoanelor impozabile înregistrate în scopuri de TVA față de decontul precompletat RO e-TVA, aplicabile și magazinelor online, conform OUG 70/2024."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum pregătesc un magazin online pentru e-TVA 2026

Sistemul RO e-TVA nu e un formular separat pe care îl completează magazinele online: e un decont de TVA **precompletat de ANAF** din datele deja transmise de firmă prin alte sisteme (e-Factura, e-Transport, SAF-T, casele de marcat), pe care persoana impozabilă trebuie să îl verifice. Pentru un magazin online, care emite un volum mare de facturi și bonuri fiscale, corelarea corectă a acestor surse înainte de depunerea decontului propriu e miza reală a „pregătirii".

## Temeiul legal

::: ghid-temei
„Articolul 12 (1) Pentru gestionarea și operaționalizarea decontului precompletat RO e-TVA, persoanele impozabile înregistrate în scopuri de TVA au următoarele obligații: a) să verifice datele și informațiile din decontul precompletat RO e-TVA transmis prin mijloace electronice; ... c) să sesizeze orice erori tehnice care rezultă din implementarea decontului precompletat RO e-TVA."
— OUG 70/2024, art. 12 alin. (1) lit. a) și c) (sursă: anaf_surse/oug_70_2024_ro_etva_decont_precompletat.txt)
:::

Obligația centrală, pentru orice persoană impozabilă înregistrată în scopuri de TVA — inclusiv un magazin online — este **verificarea** decontului precompletat, nu completarea lui de la zero. Decontul precompletat se construiește din date deja transmise de firmă către ANAF prin:

- **RO e-Factura** — facturile electronice emise/primite;
- **RO e-Transport** — transporturile rutiere de bunuri;
- **RO e-SAF-T (D406)** — fișierul standard de control fiscal;
- **RO e-Case de marcat** — bonurile fiscale raportate de AMEF-uri conectate.

Pentru un magazin online cu vânzări către consumatori (deci multe bonuri fiscale, nu doar facturi B2B), sursa AMEF e la fel de importantă ca e-Factura pentru corectitudinea decontului precompletat. Legea precizează totuși că **decontul precompletat nu constituie titlu de creanță** — el nu e un act de impunere, ci un instrument de verificare.

Litera b) a aceluiași articol, care privea obligația de a raporta discrepanțe semnificative, a fost **abrogată de la 1 ianuarie 2026** (OUG 89/2025) — o modificare recentă, utilă de reținut pentru cine a citit varianta veche a legii.

## Ce se greșește în practică

- Se tratează RO e-TVA ca pe o declarație nouă de completat, deși legal e un decont precompletat de ANAF pe care contribuabilul îl verifică și îl corelează cu propriile evidențe.
- Se ignoră sursa caselor de marcat (bonuri fiscale zilnice) la reconcilierea decontului precompletat — relevantă mai ales pentru un magazin online cu vânzări en detail, unde volumul de bonuri poate depăși cu mult numărul de facturi emise.
- Se aplică încă obligația de raportare a discrepanțelor semnificative (fosta lit. b) a art. 12), deși aceasta a fost eliminată din lege începând cu 1 ianuarie 2026.

## Ce face iConta.eu

La data acestui ghid, iConta.eu emite facturi electronice prin RO e-Factura și validează structura acestora contra validatorului oficial ANAF (vezi ghidul despre RO_CIUS), dar aplicația **nu integrează un modul dedicat pentru decontul precompletat RO e-TVA** — verificarea și corelarea decontului precompletat primit de la ANAF cu propria contabilitate rămân, la acest moment, o operațiune manuală a contabilului.

[iConta.eu](/)
