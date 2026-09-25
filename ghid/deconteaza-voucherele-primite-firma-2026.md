---
title: "Cum se decontează voucherele primite de firmă 2026"
description: "Regimul legal de decontare a biletelor de valoare (tichete de masă, cadou, cultură, vacanță) primite de o firmă de la clienți, conform Legii 165/2018."
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum se decontează voucherele primite de firmă 2026

Când o firmă acceptă de la clienți plata în tichete de masă, tichete cadou, tichete culturale sau vouchere de vacanță (colectiv, „bilete de valoare"), banii nu vin direct de la client, ci de la unitatea emitentă a biletelor, printr-un circuit reglementat strict.

## Temeiul legal

::: ghid-temei
„Articolul 7
(1) Decontarea biletelor de valoare între unitățile care acceptă aceste bilete de valoare și unitățile emitente se face numai prin intermediul unităților bancare sau prin unitățile teritoriale ale Trezoreriei Statului, după caz, potrivit legii. Același regim de decontare se va aplica și în cazul relației dintre angajator și unitatea emitentă.
(2) Sumele derulate prin operațiunile cu biletele de valoare de către unitățile emitente nu pot fi utilizate pentru reinvestirea în alte scopuri."
— Legea 165/2018 (privind acordarea biletelor de valoare), art. 7 (sursă: anaf_surse/legea_165_2018_consolidat.txt)
:::

Ce înseamnă asta pentru firma care primește vouchere de la clienți:

- **Decontarea nu se poate face în numerar sau printr-un intermediar neautorizat** — legea impune explicit circuitul prin unități bancare sau prin Trezoreria Statului, indiferent dacă biletele de valoare sunt fizice (pe hârtie) sau electronice.
- **Contravaloarea revine de la unitatea emitentă** (Up, Edenred, Sodexo etc.), nu de la client — firma trimite periodic către emitent lista biletelor de valoare încasate (fizic sau prin platformă electronică), iar emitentul virează suma corespunzătoare în contul firmei.
- Legea nu fixează un termen general de decontare — acesta se stabilește prin **contractul comercial** dintre firma acceptantă și unitatea emitentă, care de regulă include și un comision reținut de emitent.
- Biletele de valoare pe suport electronic **nu pot fi transformate în numerar** (art. 8 alin. 4) — nici de client, nici de comerciant; sumele circulă exclusiv prin conturile bancare dedicate.

## Ce se greșește în practică

- Se așteaptă ca decontarea să se facă automat, la aceeași dată în fiecare lună, fără să se verifice termenul contractual specific negociat cu unitatea emitentă — legea nu impune un termen fix, doar canalul de decontare (bancar/trezorerie).
- Se înregistrează în contabilitate valoarea integrală a biletelor acceptate ca încasare, ignorând comisionul reținut de unitatea emitentă — de fapt suma efectiv încasată e mai mică decât valoarea nominală a biletelor.
- Se acceptă bilete de valoare pentru altceva decât bunurile/serviciile pentru care au fost emise (de exemplu, tichete de masă pentru produse nealimentare) — o încălcare a art. 8 alin. (5), care limitează utilizarea biletelor la scopul pentru care au fost emise.

## Ce face iConta.eu

Modulul de beneficii din iConta.eu (`core/beneficii_api.py`) gestionează biletele de valoare din perspectiva angajatorului care le acordă salariaților (tichete de masă, cadou, cultură, creșă, vacanță), cu validările specifice fiecărui tip (de exemplu, valoarea tichetului de creșă/cultural trebuie să fie multiplu de 10 lei, conform Legii 165/2018, art. 19 și 22). La data acestui ghid, aplicația **nu acoperă latura de comerciant** — decontarea biletelor de valoare primite de la clienți ca mijloc de plată se procesează prin circuitul bancar direct cu unitatea emitentă, în afara iConta.eu; contabilul înregistrează manual în evidență sumele decontate, pe baza extraselor bancare și rapoartelor primite de la emitent.

[iConta.eu](/)
