---
title: "Cum tratez datele din jurnalul electronic al casei 2026"
description: „Jurnalul electronic" și „Raportul Z" nu sunt același document — jurnalul înregistrează fiecare operațiune în parte, în timp ce Raportul Z e doar totalul de închidere a zilei. iConta.eu citește, verificat, secțiunea de Raport Z a fișierului AMEF; nu am identificat o funcție dedicată pentru importul jurnalului electronic complet.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum tratez datele din jurnalul electronic al casei 2026

Termenul „jurnal electronic" desemnează, la o casă de marcat electronică fiscală (AMEF), înregistrarea detaliată, operațiune cu operațiune, a tot ce trece prin aparat pe parcursul zilei. Raportul Z, în schimb, e doar rezumatul de închidere — totalurile zilei fiscale, pe cote și pe tipuri de plată. Sunt două lucruri diferite, și e important să nu se confunde atunci când vine vorba de ce anume poate prelua o aplicație de contabilitate.

## Temeiul legal

::: ghid-temei
Categoria de rapoarte descrise la secțiunile II.1–II.7 din anexa tehnică „conțin datele aferente fiecărei zile fiscale încheiate" — OPANAF nr. 146/2018 pentru aprobarea structurii XML a fișierelor generate de aparatele de marcat electronice fiscale, Anexa 2
:::

Structura tehnică oficială (OPANAF 146/2018) descrie mai multe tipuri de rapoarte generate de o casă de marcat fiscală, nu doar Raportul Z — dar raportul de închidere a zilei fiscale (secțiunea II.7, element `<rB>`) este cel documentat și verificat ca fiind citit de aplicație.

## Ce citește efectiv aplicația din fișierul AMEF

Modulul de import verificat în iConta.eu parsează, dintr-un fișier semnat de casa de marcat (`.p7b` sau XML), exclusiv secțiunea de Raport Z: identificatorul casei și al raportului, totalurile pe cote de TVA, totalurile pe tipuri de plată. Aceste date sunt suficiente pentru a genera nota contabilă a zilei (vezi ghidul despre înregistrarea Raportului Z), dar **nu** reprezintă jurnalul electronic complet, cu fiecare bon/operațiune în parte.

Nu am identificat, în funcționalitatea verificată, o rută sau un ecran care să importe jurnalul electronic detaliat al casei de marcat — funcționalitatea confirmată se oprește la nivelul raportului de închidere zilnică.

## Ce se greșește în practică

- Se presupune că, odată importat Raportul Z, aplicația are acces și la jurnalul electronic complet, operațiune cu operațiune — verificat, importul acoperă doar totalurile din raportul de închidere, nu fiecare tranzacție în parte.
- Se caută în aplicație o funcție de „descărcare jurnal electronic" pentru control fiscal sau audit intern — o asemenea funcție nu a fost identificată în modulul verificat.
- Se folosește Raportul Z ca substitut pentru jurnalul electronic atunci când organul fiscal cere acces la memoria fiscală/jurnalul detaliat al casei — cele două documente au scopuri diferite și nu sunt interschimbabile.

## Ce face iConta.eu

iConta.eu importă și contabilizează datele Raportului Z — totalurile de închidere a zilei fiscale — din fișierul semnat generat de casa de marcat, conform structurii OPANAF 146/2018. Nu am identificat o funcționalitate separată, verificată, pentru citirea sau păstrarea jurnalului electronic detaliat (operațiune cu operațiune) al casei de marcat; păstrarea și accesul la acel jurnal rămân, din câte s-a putut verifica, în sarcina casei de marcat/producătorului aparatului, în afara acestui modul din aplicație.

[iConta.eu](/)
