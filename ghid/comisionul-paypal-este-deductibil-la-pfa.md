---
title: Comisionul PayPal este deductibil la PFA?
description: Comisionul reținut de PayPal poate fi dedus, dar nu pe baza unui text legal care îl numește explicit, ci prin clauza generală de deductibilitate — necesar documentul emis de platformă și legătura clară cu activitatea.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Comisionul PayPal este deductibil la PFA?

Răspunsul scurt este da, dar cu o precizare importantă: spre deosebire de comisionul bancar, care are un text de lege care îl numește direct, comisionul reținut de PayPal (sau de alt procesator de plăți nebancar) nu apare nicăieri nominalizat explicit în sursele fiscale. Deductibilitatea lui se sprijină pe clauza generală și pe condițiile standard de deductibilitate — este o interpretare cu temei solid, nu un text literal.

## Temeiul legal

::: ghid-temei
HG 1/2016 (Norme metodologice), pct. 7 alin. (5) lit. w): "alte cheltuieli efectuate în scopul realizării veniturilor."

Codul fiscal, art. 68 alin. (4): "a) să fie efectuate în cadrul activităților independente, justificate prin documente; b) să fie cuprinse în cheltuielile exercițiului financiar al anului în cursul căruia au fost plătite; ... j) să fie efectuate în scopul desfășurării activității și reglementate prin acte normative în vigoare ..."
:::

**Notă de interpretare:** sursele verificate conțin un temei explicit, numit, doar pentru comisionul *bancar* (HG 1/2016 pct. 7 alin. (5) lit. f — "cheltuielile cu comisioanele și cu alte servicii bancare"). Pentru comisionul PayPal, care nu e un serviciu bancar în acest sens, nu există o literă distinctă care să-l numească. Deducerea lui se face prin combinația dintre clauza generală de la lit. w) și condițiile generale de la art. 68 alin. (4) — mai ales lit. a) "justificate prin documente" și lit. j) "efectuate în scopul desfășurării activității". Practic, e o interpretare care se ține, dar nu e un citat literal de lege făcut pentru acest tip de comision.

## Ce contează pentru ca deducerea să reziste

Fiindcă nu există text expres, documentul justificativ contează dublu: extrasul de cont PayPal sau raportul de tranzacții care arată clar suma brută încasată, comisionul reținut și suma netă transferată. Fără acest document, condiția "justificate prin documente" de la art. 68 alin. (4) lit. a) nu este îndeplinită.

## Ce se greșește în practică

- Se deduce comisionul PayPal doar din diferența dintre suma facturată și suma primită în cont, fără niciun document care să arate explicit reținerea.
- Se presupune că regula pentru comisionul bancar (temei explicit, lit. f) se aplică identic și la PayPal — nu e același temei legal, chiar dacă rezultatul practic (deducerea) e similar.
- Nu se descarcă periodic raportul de comisioane din contul PayPal, ceea ce face imposibilă reconstituirea sumelor la un control ulterior.
- Se înregistrează în Registrul-jurnal doar suma netă primită, fără să se separe venitul brut de comisionul dedus (vezi și ghidul despre încasările prin procesator de plăți).

## Ce face iConta.eu

Validarea din `core/rip_api.py` (`_valideaza`) nu face distincție automată între tipul de comision: orice plată introdusă cu categoria `cheltuiala_deductibila` trebuie doar să aibă sumă pozitivă, dată, explicație și deductibilitate marcată — decizia de încadrare a comisionului PayPal ca deductibil rămâne a contabilului, pe baza documentului emis de platformă. Aplicația nu propune automat această categorie pentru comisioane reținute de procesatori nebancari (spre deosebire de `import_banca`, care propune implicit categoria pentru operațiunile din extrasul bancar) — introducerea și justificarea comisionului PayPal se fac manual, cu explicația și documentul aferent.

[iConta.eu](/)
