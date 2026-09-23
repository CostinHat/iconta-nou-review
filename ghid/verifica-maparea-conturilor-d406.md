---
title: Cum se verifică maparea conturilor pentru D406?
description: Verificarea reală a mapării conturilor se face prin validarea fișierului D406 cu validatorul oficial ANAF, nu printr-un pas separat de verificare.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se verifică maparea conturilor pentru D406?

Procedura oficială de depunere a D406 include un pas explicit de validare a fișierului generat, înainte de transmitere — acesta este mecanismul prin care se verifică, printre altele, și corectitudinea structurală a conturilor raportate.

## Temeiul legal

::: ghid-temei
pct. 1-9 (procedură): generare XML → validare cu "Validator" (Soft J) → generare PDF cu XML atașat, semnat electronic → transmitere prin SPV sau e-guvernare.ro. — OPANAF nr. 1783/2021, Anexa 3.
:::

Legea nu descrie o "verificare a mapării conturilor" ca pas distinct — descrie validarea întregului fișier D406 generat, cu un validator oficial, înainte de semnare și transmitere. Maparea greșită a unui cont este, în practică, unul dintre tipurile de erori pe care această validare le poate semnala, alături de alte neconcordanțe structurale.

## Ce se greșește în practică

O greșeală frecventă este tratarea validării ca pe o formalitate — se generează fișierul, se trimite direct fără a rula validarea, sau se ignoră un rezultat de validare neclar. O altă greșeală este confuzia dintre "fișierul s-a generat fără eroare" și "fișierul a fost validat" — sunt doi pași diferiți.

## Ce face iConta.eu

Validarea D406 se face cu `DUKIntegrator_AnLunaUI.jar` (`core/duk.py`, funcția `valideaza(xml, tip, an=, luna=)`), nu cu un validator generic — exact componenta oficială la care se referă procedura ANAF de mai sus.

Este utilă o precizare tehnică: a existat, istoric, un bug documentat (`DECIZII.md`, 27.07.2026) în care butonul de validare D406 nu trimitea parametrii `an`/`luna` validatorului și returna mereu o stare neconcludentă ("GRI"). Bug-ul a fost reparat, iar validarea a fost confirmată cu rezultat „valid" pe date reale (tenant_002, iunie 2026; tenant_013, 2026-08). Dacă, la un moment din trecut, ați văzut o stare de validare neclară fără explicație, mecanismul cauzei respective a fost identificat și corectat.

[iConta.eu](/)
