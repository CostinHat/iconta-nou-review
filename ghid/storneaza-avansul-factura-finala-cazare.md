---
title: "Cum se stornează avansul la factura finală pentru cazare?"
description: Regularizarea unui avans pentru servicii de cazare se face contabil, prin inversarea notei de avans, separat de emiterea facturii finale — nu există în aplicație o legătură automată între cele două documente, nici în e-Factura.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se stornează avansul la factura finală pentru cazare?

„Stornarea" avansului la o factură finală pentru cazare nu înseamnă anularea unui document — înseamnă regularizarea contabilă a avansului deja înregistrat, în paralel cu emiterea facturii finale pentru serviciul prestat efectiv.

## Temeiul legal

::: ghid-temei
„Contul 419 «Clienți - creditori» [...] În debitul contului 419 [...] se înregistrează: - decontarea avansurilor încasate de la clienți (411); [...] Soldul contului reprezintă sumele datorate clienților - creditori." — OMFP nr. 1802/2014 pentru aprobarea reglementărilor contabile
:::

Cazarea hotelieră se facturează, ca serviciu, la cota redusă de TVA de 11% (temei art. 291 alin. 2 lit. m) din Codul fiscal, aplicabil de la 1 august 2025) — cotă relevantă atât pentru avansul încasat inițial, cât și pentru factura finală.

## Cum se face regularizarea

1. **La încasarea avansului**, se generează nota `4111 = 419 + 4427`, cu TVA calculată la cota de 11% aplicabilă cazării.
2. **La factura finală**, pentru valoarea integrală a serviciului de cazare prestat, se emite factura obișnuită de vânzare (facturare standard, la cota de 11%).
3. **Regularizarea avansului** inversează nota inițială: `419 = 4111`, `4427 = 4111` — astfel încât suma avansului, deja încasată, să nu rămână dublată în evidența creanței față de client.

## Ce se greșește în practică

- Se emite factura finală pentru valoarea integrală a cazării, fără să se regularizeze avansul deja înregistrat pe contul 419 — rezultatul e o creanță/datorie rămasă incorect în evidență.
- Se presupune că regularizarea avansului se face automat, legat de factura finală, în special în e-Factura — nu există o legătură tehnică (de tip referință între documente) care să unească automat cele două facturi transmise prin SPV; fiecare document circulă independent, ca factură obișnuită.
- Se aplică o cotă de TVA diferită la factura finală față de avans (de exemplu confuzie cu vechea cotă de 9%, abrogată) — cota corectă pentru cazare, din 1 august 2025, este 11%.

## Ce face iConta.eu

iConta.eu are un mecanism dedicat pentru regularizarea avansurilor încasate (inversarea notei 419/4427 către 4111), separat de emiterea facturii finale de vânzare. Nu am identificat o funcționalitate care să lege automat, tehnic, factura de avans de factura finală în fluxul de transmitere prin e-Factura — fiecare document transmis prin SPV rămâne independent, ca factură standard, iar regularizarea contabilă a avansului rămâne o operațiune separată, făcută explicit de contabil.

[iConta.eu](/)
