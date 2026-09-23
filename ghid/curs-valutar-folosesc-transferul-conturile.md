---
title: "Ce curs valutar folosesc la transferul între conturile proprii?"
description: Orice mișcare de valută între conturile proprii ale firmei se înregistrează, ca regulă contabilă generală, la cursul BNR de la data operațiunii — dacă suma efectiv primită diferă (bancă a aplicat propriul curs de schimb), diferența se recunoaște ca venit sau cheltuială din curs valutar.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Ce curs valutar folosesc la transferul între conturile proprii?

Un transfer între conturile bancare proprii ale firmei — de exemplu, dintr-un cont în lei către un cont în valută, sau invers — e o operațiune care trebuie evaluată în lei ca orice altă tranzacție în valută. Regula contabilă generală e simplă: cursul de referință e cel BNR, comunicat pentru data operațiunii, indiferent că e vorba de o factură, o plată către furnizor sau o mișcare internă de trezorerie.

## Temeiul legal

::: ghid-temei
„O tranzacție în valută trebuie înregistrată inițial la cursul de schimb valutar, comunicat de Banca Națională a României, de la data efectuării operațiunii." — OMFP 1802/2014 (Reglementările contabile), pct. 319.
:::

## Regula pentru un transfer între conturi proprii

Dacă transferul e o simplă mutare de sume în aceeași monedă între două conturi ale firmei (de exemplu, EUR–EUR, la bănci diferite), nu apare o problemă de curs — suma transferată e aceeași, doar contul se schimbă.

Dacă transferul implică o conversie efectivă de monedă (de exemplu, RON către EUR, prin schimb valutar la bancă), operațiunea se înregistrează la cursul BNR din data operațiunii, conform pct. 319. Suma efectiv primită în contul valutar poate diferi de cea rezultată din cursul BNR, pentru că băncile comerciale aplică propriul curs de schimb (de vânzare/cumpărare valută), de regulă mai puțin favorabil decât cursul de referință BNR. Diferența dintre suma contabilizată la curs BNR și suma efectiv primită la cursul băncii se recunoaște ca diferență de curs valutar (venit sau cheltuială, conturile 765/665), aceeași logică folosită și la decontarea creanțelor și datoriilor în valută.

## Ce se greșește în practică

- Se contabilizează transferul direct la suma primită de la bancă, fără să se verifice dacă aceasta corespunde cursului BNR al zilei — diferența de curs rămâne astfel „ascunsă" în soldul contului, în loc să fie recunoscută separat ca venit/cheltuială financiară.
- Se presupune că un transfer intern (fără o factură sau o decontare de creanță/datorie în spate) nu are curs valutar aplicabil — regula pct. 319 nu face excepție pentru simpla mutare de fonduri, dacă are loc o conversie efectivă de monedă.
- Se confundă cursul BNR (folosit pentru evidența contabilă) cu cursul comercial al băncii (folosit efectiv la schimbul valutar) — cele două sunt surse diferite, iar diferența dintre ele nu e o eroare, ci un rezultat financiar normal de recunoscut.

## Ce face iConta.eu

Motorul de curs (`core/curs_bnr.py`) oferă ultimul curs BNR comunicat, valabil la data operațiunii, ca sursă unică de referință pentru orice operațiune în valută introdusă în aplicație — inclusiv liniile de extras bancar. Suma efectiv contabilizată pentru o linie de extras vine din extrasul importat, nu dintr-un calcul automat de conversie RON↔valută la momentul transferului — dacă apare o diferență între suma din extras și valoarea la curs BNR, înregistrarea diferenței de curs (665/765) rămâne o operațiune separată, făcută de contabil pe baza extraselor celor două conturi.

[iConta.eu](/)
