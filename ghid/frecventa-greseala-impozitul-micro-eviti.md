---
title: "Cea mai frecventă greșeală la impozitul micro: cum o eviți"
description: Capcana conceptuală tipică e calcularea impozitului micro din profit (venituri minus cheltuieli), ca la impozitul pe profit — legea îl calculează direct din venituri brute, cu doar câteva excluderi explicite, fără să scadă nicio cheltuială.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cea mai frecventă greșeală la impozitul micro: cum o eviți

Nu există o statistică oficială care să clasifice greșelile la impozitul micro, dar dintre cele verificate direct în lege și în mecanismul de calcul, una revine constant, mai ales la firme care vin din regimul de impozit pe profit sau confundă cele două logici: aplicarea unui raționament de „profit" acolo unde legea cere un calcul direct pe „venituri".

## Temeiul legal

::: ghid-temei
„Cota de impozit pe veniturile microîntreprinderilor este de 1%." — Codul fiscal, art. 51 alin. (1), de la 1 ianuarie 2026. Baza impozabilă o reprezintă „veniturile din orice sursă", din care se scad **doar** categoriile enumerate la art. 53 alin. (1) lit. a)-o) — nu cheltuielile firmei.
:::

## Greșeala: calculul din profit, nu din venituri

La impozitul pe profit, baza de calcul e rezultatul contabil (venituri minus cheltuieli), ajustat fiscal. La impozitul micro, baza e **veniturile**, fără nicio scădere de cheltuieli — impozitul de 1% se aplică direct pe cifra de venituri din trimestru (70x+75x+76x, minus 709), din care se elimină doar categoriile explicit excluse de art. 53 alin. (1). O firmă cu cheltuieli mari și profit mic (sau chiar pierdere) tot datorează impozit micro pe veniturile ei — regula nu ține cont de profitabilitate.

## Ce se greșește în practică

- Se scad din bază cheltuieli deductibile fiscal (ca la profit), deși impozitul micro nu are conceptul de „cheltuială deductibilă" — doar veniturile enumerate la art. 53 alin. (1) ies din bază.
- Se omite scăderea contului 709 (reduceri comerciale acordate) din baza de calcul, umflând veniturile impozabile.
- Se includ în bază venituri explicit excluse de lege (diferențe de curs valutar, venituri financiare legate de creanțe/datorii în valută — art. 53 alin. (1) lit. h)/i)), din prezumția că „orice venit din balanță" intră automat în calcul.

## Cum se evită

Calculul corect pornește mereu de la venituri, nu de la profit: se identifică soldul creditor al conturilor 70x, 75x, 76x, se scade debitul contului 709, se scad categoriile de la art. 53 alin. (1) care se aplică situației concrete a firmei, iar rezultatul se înmulțește cu 1%. Cheltuielile firmei nu intră deloc în această formulă.

## Ce face iConta.eu

Motorul de calcul (`core/d100.py`) aplică exact această logică: baza impozabilă vine din soldurile creditoare ale conturilor 70x, 75x, 76x, minus debitul contului 709, fără nicio scădere de cheltuieli, iar impozitul rezultă din înmulțirea cu 1%. Nu există, în acest calcul, niciun pas care să scadă cheltuieli deductibile — aplicația urmează strict logica „pe venituri" a legii, nu logica „pe profit" a impozitului pe profit.

[iConta.eu](/)
