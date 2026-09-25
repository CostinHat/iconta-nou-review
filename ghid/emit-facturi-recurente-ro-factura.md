---
title: "Cum emit facturi recurente prin RO e-Factura?"
description: "Facturile emise periodic, pentru abonamente sau chirii, urmează aceleași reguli de transmitere prin RO e-Factura ca orice altă factură, inclusiv termenul legal de transmitere."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum emit facturi recurente prin RO e-Factura?

O factură recurentă (abonament, chirie, serviciu lunar) nu are un regim special în RO e-Factura — este, din punct de vedere legal, o factură ca oricare alta, supusă acelorași termene de emitere și transmitere.

## Temeiul legal

::: ghid-temei
„Termenul-limită pentru transmiterea facturilor în sistemul naţional privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii, dar nu mai târziu de 5 zile lucrătoare de la data-limită pentru emiterea facturii prevăzută la art. 319 alin. (16) din Legea nr. 227/2015, cu modificările şi completările ulterioare. Calculul termenului-limită se efectuează conform Regulamentului (CEE, Euratom) nr. 1182/71 al Consiliului din 3 iunie 1971 privind stabilirea regulilor care se aplică termenelor, datelor şi expirării termenelor."
— OUG nr. 120/2021, art. 10 alin. (7), astfel cum a fost modificat prin OUG nr. 89/2025 (sursă: anaf_surse/oug_89_2025.txt)
:::

Pentru facturile emise periodic, din șabloane, termenul funcționează la fel ca pentru orice factură individuală:

- **5 zile lucrătoare de la data emiterii** fiecărei facturi generate automat — nu contează că factura provine dintr-un șablon recurent, ceasul termenului pornește de la data emiterii ei concrete.
- Termenul nu poate depăși **5 zile lucrătoare de la data-limită legală de emitere** a facturii, stabilită la art. 319 alin. (16) din Codul fiscal (de regulă, cel târziu până în a 15-a zi a lunii următoare celei în care a intervenit faptul generator) — două limite care lucrează împreună, nu una singură.
- O facturare recurentă emisă cu întârziere față de data-limită legală de emitere nu capătă un termen suplimentar de transmitere — cele două termene de 5 zile lucrătoare se calculează independent, iar depășirea celui legat de data-limită de emitere rămâne o abatere, indiferent de motivul întârzierii.

## Ce se greșește în practică

- Se presupune că facturile recurente, fiind generate automat, sunt exceptate de la termenul de 5 zile lucrătoare — legea nu prevede nicio derogare pentru facturile emise din șabloane.
- Se acumulează mai multe facturi recurente generate în aceeași zi și se transmit „la pachet" mai târziu, depășind termenul pentru cele mai vechi dintre ele.
- Se ignoră a doua limită a termenului (legată de data-limită de emitere din art. 319 alin. (16) Cod fiscal), presupunând că doar data emiterii efective contează.

## Ce face iConta.eu

iConta.eu are un modul funcțional de facturi recurente (`core/facturi_recurente.py`), care emite automat, printr-un job zilnic (`core/cron.py`), facturile din șabloanele active a căror zi de emitere configurată a fost atinsă și care nu au mai fost emise în luna curentă. Fiecare factură astfel generată intră în fluxul obișnuit de transmitere prin RO e-Factura (`core/efactura_send.py`), fără tratament diferit față de o factură emisă manual — deci termenul legal de 5 zile lucrătoare de la emitere se aplică identic.

[iConta.eu](/)
