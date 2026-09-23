---
title: Cum verific facturile primite după închiderea lunii
description: iConta.eu are două mecanisme distincte legate de facturile primite și închiderea lunii — poarta care oprește scrierile (Blocare perioade) și verificarea de completitudine care refuză să declare luna închisă dacă mai sunt e-Facturi neînregistrate. Nu sunt duplicate.
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Cum verific facturile primite după închiderea lunii

„Închiderea lunii" înseamnă, în iConta.eu, două lucruri diferite, ușor de confundat: **Blocarea perioadelor** (poarta care oprește orice scriere contabilă pe luna respectivă) și **verificarea de completitudine pe facturi**, care refuză motivat să declare luna „încheiată pe facturi" dacă mai există e-Facturi primite neînregistrate. Prima e o poartă dură; a doua e o afirmație despre stadiul evidenței — și tocmai a doua e cea care te ajută să verifici facturile primite.

## Temeiul legal

::: ghid-temei
„Dreptul de deducere ia naștere la momentul exigibilității taxei." — Codul fiscal, art. 297 alin. (1)

„În situația în care nu sunt îndeplinite condițiile și formalitățile de exercitare a dreptului de deducere în perioada fiscală de declarare (...), persoana impozabilă își poate exercita dreptul de deducere prin decontul perioadei fiscale în care sunt îndeplinite aceste condiții și formalități sau printr-un decont ulterior, dar în cadrul termenului de prescripție prevăzut în Codul de procedură fiscală." — Codul fiscal, art. 301 alin. (2)

„Corectarea erorilor se efectuează la data constatării lor." — OMFP 1802/2014, Anexa 1 – Reglementări contabile (formă consolidată), pct. 65 alin. (2)
:::

TVA-ul unei facturi de furnizor sosite târziu se deduce în perioada în care e primită, în termenul de prescripție de 5 ani — nu se rectifică decontul din luna la care se referă factura. Cheltuiala în sine urmează regula corectării erorilor: la data constatării, nu la data documentului.

## Ce verifică efectiv aplicația

**1. Verificarea de completitudine (`inchidere_luna`).** Când se încearcă blocarea unei luni din Registru jurnal, iConta.eu verifică dacă mai există e-Facturi primite de la ANAF (prin SPV) și rămase neînregistrate — nici ciornă, nici validate, nici respinse — cu data în luna respectivă. Dacă găsește așa ceva, **refuză blocarea**, cu un mesaj care spune câte documente și unde se rezolvă. Practic, e verificarea pe care o poți folosi înainte de a bloca luna, ca să te asiguri că n-a rămas nimic nepreluat din e-Factura.

**2. Poarta de blocare propriu-zisă (F118).** Odată luna blocată, orice înregistrare nouă pe acea lună — inclusiv contarea unei facturi rămase neînregistrată — e respinsă de un trigger de bază de date, indiferent de sursă (UI, import, cron). Mesajul arătat: *„Perioada e blocată (luna închisă). Cere-i administratorului cabinetului să o redeschidă sau înregistrează în luna curentă."*

Cele două sunt legate operațional — blocarea lunii (pasul 2) verifică chiar ea completitudinea din pasul 1 înainte de a permite închiderea — dar rămân mecanisme diferite: unul e o poartă care oprește scrieri, celălalt e o constatare despre stadiul evidenței.

## Ce se face dacă o factură primită scapă și verificarea

Verificarea de completitudine acoperă doar ce a coborât din e-Factura. O factură primită pe alt canal (hârtie, e-mail) nu declanșează refuzul de la pasul 1, deci luna se poate bloca fără ea. Dacă o astfel de factură apare ulterior, contarea ei nu se poate face cu data facturii (luna e blocată) — se contează cu o dată explicită, la momentul descoperirii, cu motivul consemnat în notă.

## Ce se greșește în practică

- Se confundă „am blocat luna, deci evidența e completă" cu realitatea — blocarea nu verifică nimic la momentul scrierii ei, doar respinge orice scriere ulterioară. Completitudinea e verificată *înainte*, la încercarea de blocare, nu garantată de blocarea în sine.
- Se rectifică decontul de TVA din luna facturii, deși legea permite deducerea în perioada în care factura a fost efectiv primită, în termenul de prescripție.
- Se ignoră faptul că verificarea automată acoperă strict e-Factura — o factură primită pe hârtie sau prin e-mail rămâne responsabilitatea contabilului de a o căuta manual, înainte de a bloca luna.

## Ce face iConta.eu

La încercarea de blocare a unei luni, aplicația verifică e-Facturile primite și rămase neînregistrate cu data în acea lună și refuză motivat blocarea dacă găsește vreuna — cu numărul lor și direcția în care se rezolvă. Odată luna blocată, orice scriere nouă e respinsă de trigger-ul de bază de date, indiferent de sursă. O factură primită pe alt canal decât e-Factura și găsită după blocare nu se poate contabiliza cu data ei originală — se înregistrează cu data descoperirii, cu mențiunea explicită a motivului, iar TVA-ul rămâne deductibil în perioada primirii, în termenul legal de prescripție.

[iConta.eu](/)
