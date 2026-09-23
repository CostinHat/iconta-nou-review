---
title: Validarea VIES pentru partenerii intracomunitari: pași
description: Pașii verificării unui partener din UE în iConta.eu — de la separarea codului de TVA până la rezultatul afișat la emiterea facturii — și ce înseamnă fiecare stare posibilă: valid, invalid sau VIES indisponibil.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Validarea VIES pentru partenerii intracomunitari: pași

Verificarea VIES nu e un pas opțional de bifat „ca să fie” — e condiția de fond a tratamentului fiscal favorabil, atât pentru livrări/prestări (scutire, respectiv neimpozabilitate în România), cât și pentru achiziții (taxare inversă corectă). Pașii de mai jos descriu exact ce se întâmplă tehnic, în ordine.

## Temeiul legal

::: ghid-temei
„`verifica_vies(cod_tva, timeout=15)` — interoghează `https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{MS}/vat/{nr}`, întoarce `{valid, nume, adresa, tara, numar, eroare}`.” — cod sursă `core/intracomunitar.py`, verificat în dosarul F050; folosit pentru condiția „cod TVA valid” din CF art. 294 alin. (2) lit. a) (livrări) și art. 278 alin. (2) (servicii B2B).
:::

## Pas cu pas

**1. Introduci codul de TVA al partenerului**, cu prefixul de țară inclus — de exemplu „DE123456789”, nu doar „123456789”.

**2. Sistemul separă prefixul de restul codului** și îl validează contra listei statelor membre recunoscute pentru VIES (cele 27 + „XI” pentru Irlanda de Nord). Grecia e normalizată automat: prefixul legal e „EL”, nu „GR”.

**3. Dacă forma e corectă, se interoghează live serviciul REST oficial VIES** al Comisiei Europene, cu un timeout de verificare — dacă serviciul nu răspunde la timp, rezultatul e un avertisment explicit, nu o presupunere de validitate.

**4. Rezultatul afișat e unul din trei:** cod valid (cu numele și adresa firmei, dacă statul membru le publică), cod invalid, sau „VIES indisponibil” — caz în care verificarea trebuie reluată, pentru că nu s-a putut confirma nimic.

**5. Rezultatul decide tratamentul operațiunii**: la livrare/prestare, cod valid înseamnă scutire (bunuri) sau neimpozabilitate în România cu declarare D390 (servicii); cod invalid înseamnă facturare cu TVA românesc, ca operațiune internă.

## Ce se greșește în practică

Sărirea peste pasul 3 la a doua sau a treia operațiune cu același partener, pe motiv că „l-am verificat deja” — validitatea se schimbă în timp, iar ce contează e starea la data fiecărei operațiuni, nu la prima verificare din relația comercială. A doua greșeală frecventă: tratarea unui rezultat „VIES indisponibil” ca implicit favorabil — e absența unui răspuns, nu o confirmare.

## Ce face iConta.eu

Verificarea rulează automat la emiterea unei facturi către un client cu cod de TVA de prefix non-românesc — nu e un buton separat de apăsat manual de fiecare dată, ci parte din fluxul normal de emitere. Rezultatul (valid/invalid/indisponibil) se afișează direct pe ecran, iar erorile de formă a codului (absent, prefix nevalid, prefix fără număr) sunt distincte de eroarea de validitate — deci mesajul arată exact unde e problema.

[iConta.eu](/)
