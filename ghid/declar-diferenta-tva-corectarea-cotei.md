---
title: "Cum declar diferența de TVA după corectarea cotei?"
description: "Corectarea unei cote de TVA aplicate greșit pe o factură urmează regulile Codului fiscal pentru facturi de corecție, iar diferența de taxă se reflectă în decontul perioadei în care se emite corecția."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum declar diferența de TVA după corectarea cotei?

Dacă descoperi că ai aplicat cota greșită de TVA pe o factură deja emisă (de exemplu 9% în loc de 19%, sau invers), corectarea nu se face „retroactiv" în decontul deja depus, ci printr-o factură de corecție, iar diferența de taxă intră în decontul din perioada în care emiți corecția.

## Temeiul legal

::: ghid-temei
„(4) În cazul taxei pe valoarea adăugată, corectarea erorilor din deconturile de taxă se realizează potrivit prevederilor Codului fiscal. Erorile materiale din decontul de taxă pe valoarea adăugată se corectează potrivit procedurii aprobate prin ordin al președintelui A.N.A.F."
— Legea nr. 207/2015 (Codul de procedură fiscală), art. 105 alin. (4) (sursă: anaf_surse/legea_207_2015_consolidat.txt)
:::

- Corectarea unei cote de TVA greșite pe o factură se face prin **factură de corecție** (stornare + factură nouă, sau notă de corecție, după caz), nu prin modificarea directă a decontului deja depus.
- Diferența de TVA rezultată din corecție (fie ea în plus, fie în minus) se declară în **decontul de TVA aferent perioadei fiscale în care se emite corecția**, nu prin refacerea decontului din perioada facturii inițiale.
- Dacă eroarea e strict **materială** (de exemplu o cifră greșită introdusă în formular, fără să existe o eroare de fond în tratamentul TVA), corectarea urmează procedura specială aprobată prin ordin al președintelui ANAF, mai simplă decât o rectificativă completă.
- Pentru erori de fond (cotă greșit aplicată, operațiune greșit încadrată), corectarea trece prin regulile generale ale Codului fiscal pentru ajustarea bazei de impozitare, cu factură de corecție către partener.

## Ce se greșește în practică

- Se depune o declarație D300 rectificativă pentru perioada facturii inițiale, deși eroarea de cotă TVA se corectează prin factură de corecție reflectată în decontul curent, nu prin rescrierea deconturilor vechi.
- Se tratează orice corecție de TVA ca „eroare materială", încercând procedura simplificată ANAF, deși o cotă greșit aplicată e o eroare de fond, nu o simplă greșeală de tastare.
- Se omite emiterea facturii de corecție către partener, înregistrând doar intern diferența de TVA — fără document, ajustarea nu e opozabilă și poate fi respinsă la un control.

## Ce face iConta.eu

La data acestui ghid, modulul de facturare din iConta.eu permite emiterea facturilor de stornare/corecție și integrarea lor în jurnalul de vânzări, iar modulul D300 (`core/d300.py`, `core/d300_reconciliere.py`) preia automat operațiunile din perioada curentă, inclusiv corecțiile emise atunci. Aplicația nu are însă un asistent dedicat care să distingă automat între „eroare materială" (cu procedura simplificată ANAF) și corectare de fond a cotei TVA — încadrarea corectă a tipului de eroare și emiterea documentului potrivit rămân în sarcina contabilului.

[iConta.eu](/)
