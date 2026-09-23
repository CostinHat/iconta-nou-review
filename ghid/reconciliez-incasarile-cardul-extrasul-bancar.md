---
title: "Cum reconciliez încasările cu cardul cu extrasul bancar?"
description: Reconcilierea automată funcționează bine cât timp fiecare linie din extras are un CUI de client lizibil și o sumă egală cu factura — pe sume cumulate de la mai mulți clienți sau depuneri nete de comision, potrivirea automată nu se aplică.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum reconciliez încasările cu cardul cu extrasul bancar?

Dacă o plată cu cardul ajunge în extrasul bancar ca linie distinctă, cu CUI-ul clientului lizibil în descriere și cu o sumă egală cu factura, reconcilierea automată o potrivește la fel ca orice altă încasare bancară. Problemele apar când procesatorul de card grupează sau modifică suma depusă.

## Temeiul legal

::: ghid-temei
„Pentru operațiunile economice pentru care, conform prevederilor Codului fiscal, nu există obligația întocmirii facturii, înregistrarea în contabilitate a acestora se efectuează pe baza contractelor încheiate între părți și a documentelor financiar-contabile sau bancare care să ateste acele operațiuni, cum sunt: aviz de însoțire a mărfii, chitanță, dispoziție de plată/încasare, extras de cont bancar, notă de contabilitate etc." — OMFP nr. 2634/2015, Anexa 1, pct. 25
:::

Extrasul de cont e documentul justificativ pe care se sprijină înregistrarea încasării — indiferent dacă banii au ajuns direct de la client sau printr-un procesator de card intermediar, ceea ce contează contabil e suma reală atestată de extras.

## Ce funcționează automat și ce nu

- **Funcționează**: o linie de extras cu CUI-ul clientului identificabil în descriere și sumă egală cu o factură (sau o combinație de facturi) a aceluiași client — reconcilierea o potrivește exact, ca pe orice altă încasare bancară.
- **Nu funcționează automat**: motorul de potrivire cere un CUI unic pe linie. Un decont de card care vine ca **sumă cumulată pe mai mulți clienți** (tipic pentru vânzări cu amănuntul) nu are un CUI unic de identificat și nu se potrivește automat.
- **Nu funcționează automat**: dacă procesatorul depune suma **netă de comision** (mai mică decât totalul facturii), potrivirea exactă eșuează, iar linia poate cădea pe potrivire parțială sau fără potrivire, pentru că reconcilierea nu separă automat comisionul din sumă.

## Ce se greșește în practică

- Se așteaptă ca reconcilierea automată să funcționeze la fel pentru toate încasările cu cardul, indiferent dacă vin ca sumă individuală (cu CUI) sau ca sumă cumulată pe zi/lot (fără CUI unic).
- Se lasă neexplicată diferența dintre suma facturată clientului și suma netă depusă de procesator — comisionul reținut trebuie înregistrat separat, ca o cheltuială distinctă, nu ignorat.
- Se contabilizează suma din extras ca fiind încasarea integrală a facturii, deși ea reprezintă suma netă — diferența (comisionul) rămâne nealocată nicăieri.

## Ce face iConta.eu

iConta.eu potrivește automat orice linie de extras care conține CUI-ul unui client și o sumă (exactă sau printr-o combinație de facturi) egală cu facturile lui deschise — mecanismul e identic pentru încasările cu cardul care ajung astfel în extras. Pentru decontări cumulate pe mai mulți clienți sau depuneri nete de comision, aplicația nu are, la acest moment, un flux automat dedicat de separare a comisionului sau de descompunere a sumei pe clienți — alocarea trebuie făcută manual, prin alegerea facturilor din picker-ul de reconciliere, iar comisionul înregistrat separat printr-o notă de cheltuială.

[iConta.eu](/)
