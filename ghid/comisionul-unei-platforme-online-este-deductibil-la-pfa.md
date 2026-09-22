---
title: Comisionul unei platforme online este deductibil la PFA?
description: Comisionul reținut de o platformă (marketplace, procesator de plăți, aplicație de intermediere) este deductibil prin clauza generală "alte cheltuieli efectuate în scopul realizării veniturilor", nu printr-un text care îl numește direct.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Comisionul unei platforme online este deductibil la PFA?

Pentru un PFA care vinde printr-un marketplace, primește plăți printr-un procesator online sau lucrează printr-o aplicație de intermediere, comisionul reținut de platformă este, în principiu, o cheltuială deductibilă. Important de știut: acest tip de comision nu are un text de lege dedicat, așa cum are comisionul bancar — deductibilitatea lui se argumentează prin clauza generală și prin condițiile standard, nu printr-un citat literal.

## Temeiul legal

::: ghid-temei
HG 1/2016 (Norme metodologice), pct. 7 alin. (5) lit. w): "alte cheltuieli efectuate în scopul realizării veniturilor."

Codul fiscal, art. 68 alin. (4): "a) să fie efectuate în cadrul activităților independente, justificate prin documente; b) să fie cuprinse în cheltuielile exercițiului financiar al anului în cursul căruia au fost plătite; ... j) să fie efectuate în scopul desfășurării activității și reglementate prin acte normative în vigoare ..."
:::

**Notă de interpretare:** în sursele verificate, temei explicit, numit textual, există doar pentru comisionul *bancar* (HG 1/2016 pct. 7 alin. (5) lit. f). Pentru comisioanele reținute de platforme de tip marketplace, aplicații de curierat/livrare, platforme de freelancing sau alți intermediari online, singurul sprijin legal e clauza generală de la lit. w), combinată cu condițiile generale de deductibilitate de la art. 68 alin. (4) lit. a) și j). Este o deducere susținută, dar bazată pe interpretare, nu pe un text care numește explicit "comisionul de platformă".

## Ce document face diferența

Fiindcă nu există literă de lege dedicată, documentul justificativ emis de platformă (factură de comision, raport de vânzări cu comisionul detaliat, extras de tranzacții) devine elementul-cheie care susține deducerea în fața unui control. Fără el, condiția "justificate prin documente" nu e îndeplinită și deducerea poate fi contestată.

::: ghid-exemplu
Un PFA vinde printr-un marketplace care reține automat 12% comision din fiecare comandă. La finalul lunii, platforma emite un raport cu vânzările brute și comisionul total reținut. Suma brută a vânzărilor se înregistrează ca încasare (categoria "activitate"), iar comisionul reținut se înregistrează separat, ca plată, la categoria "cheltuiala_deductibila", cu raportul platformei ca document justificativ.
:::

## Ce se greșește în practică

- Se înregistrează în Registrul-jurnal doar suma netă primită de la platformă, fără să se evidențieze separat venitul brut și comisionul (vezi și ghidul despre încasările prin procesator de plăți).
- Se presupune, greșit, că orice comision reținut de o platformă are același temei legal explicit ca cel bancar.
- Nu se descarcă/păstrează raportul lunar de comisioane al platformei, document esențial în lipsa unui text de lege dedicat.
- Se amestecă în aceeași categorie comisionul de platformă cu alte taxe reținute de aceeași platformă care ar putea fi nedeductibile (de exemplu penalități de întârziere la livrare).

## Ce face iConta.eu

`core/rip_api.py` nu tratează diferit, la nivel de cod, comisionul unei platforme online față de alt tip de cheltuială: orice plată introdusă cu categoria `cheltuiala_deductibila` trece prin aceeași validare (`_valideaza`) — sumă pozitivă, dată, explicație, deductibilitate marcată. Decizia de a încadra comisionul de platformă ca deductibil, pe baza documentului emis de platformă, rămâne integral a contabilului. Spre deosebire de operațiunile importate automat din extrasul bancar (`import_banca`, unde categoria e propusă implicit), comisioanele reținute direct de o platformă (fără să treacă prin extrasul bancar ca linie separată) se introduc și se justifică manual în registru.

[iConta.eu](/)
