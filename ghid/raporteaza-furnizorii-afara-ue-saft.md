---
title: "Cum se raportează furnizorii din afara UE în SAF-T?"
description: Diferența dintre codurile de identificare 00 (România), 01 (Uniunea Europeană) și 02 (afara UE) din nomenclatorul SAF-T, și cum se raportează corect un furnizor din afara UE.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Cum se raportează furnizorii din afara UE în SAF-T?

La fel ca partenerii interni, furnizorii din afara Uniunii Europene au un cod dedicat în structura SAF-T — diferit atât de codul folosit pentru un furnizor român, cât și de cel pentru un furnizor din UE. Nu e o distincție cosmetică: schema separă explicit spațiul intracomunitar de restul lumii.

## Temeiul legal

::: ghid-temei
„MasterFiles ... Conţine date preluate din Registrul-jurnal, furnizori, clienţi, produse, stocuri, active etc." — OPANAF nr. 1783/2021, Anexa 1, pct. 4-5.

Subsecțiunea Suppliers (furnizori) din MasterFiles identifică fiecare partener printr-un cod de tip, parte din nomenclatorul tehnic al schemei publicat de ANAF alături de schema XSD.
:::

## Cele trei coduri pentru un partener cu personalitate juridică

Nomenclatorul de identitate al partenerilor distinge explicit trei situații, în funcție de originea partenerului:

- **00** + CUI — partener persoană juridică din România;
- **01** + cod fiscal — operator din Uniunea Europeană;
- **02** + cod fiscal — operator din afara Uniunii Europene (extra-UE).

Codul „00" e rezervat exclusiv partenerilor din România — nu e un cod generic pentru „intern" extins și la UE. Un furnizor din, de exemplu, Elveția, Regatul Unit sau Turcia se raportează cu codul **02**, nu cu 01 și nu cu 00. Diferența dintre 01 și 02 contează pentru că schema tratează separat operatorii intracomunitari de cei din afara Uniunii, chiar dacă ambii sunt „străini" din perspectivă românească.

## Ce se greșește în practică

- Se folosește codul 00 (rezervat României) pentru orice partener fără CUI românesc, indiferent de origine.
- Se confundă „extra-UE" cu „UE" — un furnizor din afara Uniunii (cod 02) nu se tratează identic cu unul intracomunitar (cod 01).
- Se lasă identificatorul partenerului pe formatul brut, fără prefixul de tip (00/01/02), ceea ce nu respectă structura oficială a nomenclatorului.

## Ce face iConta.eu

iConta.eu determină automat codul de tip al partenerului — 00 pentru România, 01 pentru Uniunea Europeană, 02 pentru operatori din afara UE — din datele lui, fără introducere manuală pe fiecare factură. Identificarea a fost reparată explicit în cod (anterior emisă ca identificator brut, fără prefix de tip) și e gardată la emitere.

[iConta.eu](/)
