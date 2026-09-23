---
title: "Raportul Z corelat cu plafonul de numerar 2026"
description: Plafoanele de numerar din Legea 70/2015 se verifică pe soldul din Registrul de casă, iar Registrul de casă nu preia automat numerarul din Raportul Z — deci corelarea celor două rămâne, deocamdată, o verificare manuală.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Raportul Z corelat cu plafonul de numerar 2026

Vânzările încasate în numerar printr-o casă de marcat pot intra sub incidența plafoanelor legale de numerar — mai ales plafonul de casă zilnic („cash & carry"). Problema practică e că motorul de verificare a plafoanelor din aplicație lucrează pe soldul Registrului de casă, iar numerarul din Raportul Z nu ajunge automat acolo.

## Temeiul legal

::: ghid-temei
Plafoanele de numerar aplicabile — plafonul de casă („cash & carry") de 500.000 lei și plafoanele de încasare/plată de 5.000 lei, respectiv 10.000 lei către/de la o persoană juridică — sunt cele stabilite prin Legea nr. 70/2015, astfel cum a fost actualizată prin Legea nr. 239/2025 (în vigoare de la 1 ianuarie 2026).
:::

## Cum sunt aplicate plafoanele în aplicație

Motorul de verificare a plafoanelor (folosit de modulul Registrului de casă din iConta.eu) operează cu aceste valori — 500.000 lei plafon de casă și 5.000/10.000 lei plafon de încasare/plată per persoană juridică — verificate direct pe operațiunile înregistrate în Registrul de casă al aplicației.

Aici intervine, însă, aceeași limitare descrisă și la înregistrarea Raportului Z: modulul Registrului de casă citește exclusiv din evidența proprie de operațiuni de casierie (categorii fixe: încasare client, plată furnizor, ridicare/depunere bancă, avans spre decontare) — **nu** și din notele contabile generate automat de Raportul Z (import AMEF sau introducere manuală). Prin urmare, verificarea automată a plafonului nu „vede" automat numerarul dintr-un Raport Z, dacă acea sumă nu a fost introdusă și ca operațiune în Registrul de casă.

## Ce se greșește în practică

- Se presupune că verificarea plafonului de casă din aplicație include automat și numerarul din vânzările cu Raport Z — motorul de plafoane verifică doar ce e efectiv înregistrat în Registrul de casă, iar Raportul Z nu scrie acolo automat.
- Se aplică plafonul de 5.000/10.000 lei (încasare/plată către o persoană juridică) la vânzările cu amănuntul din Raportul Z, către persoane fizice — acest plafon vizează raporturile cu o persoană juridică, nu vânzările obișnuite prin casa de marcat către consumatori persoane fizice; confuzia între cele două plafoane duce la concluzii greșite.
- Se ignoră complet verificarea plafonului de casă pentru firmele cu încasări mari prin casa de marcat, presupunând că „numerarul din vânzări nu se pune la plafon" — plafonul de casă se raportează la soldul efectiv de numerar, indiferent de sursă.

## Ce face iConta.eu

iConta.eu are, în modulul Registrului de casă, un motor de verificare a plafoanelor conform Legii 70/2015 (actualizată, în vigoare 2026): plafon de casă 500.000 lei, plafon 5.000/10.000 lei pentru operațiuni cu persoane juridice. Acest motor verifică soldul și operațiunile înregistrate efectiv în Registrul de casă. Pentru că numerarul din Raportul Z nu ajunge automat în această evidență (vezi și ghidul despre înregistrarea Raportului Z în registrul de casă), corelarea corectă a plafonului cu vânzările prin casa de marcat presupune, deocamdată, introducerea manuală a acelor sume ca operațiuni de casierie, dacă firma vrea ca motorul de plafoane să le ia în calcul.

[iConta.eu](/)
