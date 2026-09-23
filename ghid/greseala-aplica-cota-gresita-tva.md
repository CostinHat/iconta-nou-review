---
title: "Greșeala de a aplica cota greșită de TVA"
description: "Cota de TVA greșită are de fapt două cauze diferite, care cer remedii diferite: o eroare de perioadă (cota veche folosită după schimbarea legală) sau o eroare de încadrare a produsului (11% în loc de 21%, sau invers). Multe firme le tratează la fel — și greșesc de două ori."
published: 2026-09-23
modified: 2026-09-23
poarta: v1
---

# Greșeala de a aplica cota greșită de TVA

„Am aplicat cota greșită de TVA" ascunde, de fapt, două erori diferite, care nu se corectează la fel și nici nu se detectează la fel. Confuzia dintre ele e ea însăși partea cea mai costisitoare a greșelii, pentru că duce la o falsă senzație de siguranță: „am verificat, e în regulă" — când, de fapt, doar unul din cele două tipuri de eroare a fost verificat.

## Temeiul legal

::: ghid-temei
**Art. 291 alin. (1):** „Cota standard se aplică asupra bazei de impozitare pentru operațiunile impozabile care nu sunt scutite de taxă sau care nu sunt supuse cotei reduse, iar nivelul acesteia este 21%."

**Art. 291 alin. (2):** „Cota redusă de 11% se aplică asupra bazei de impozitare pentru următoarele prestări de servicii și/sau livrări de bunuri:" — urmată de lista limitativă lit. a)-n).

**Art. 330 alin. (1):** corectarea unei facturi cu date greșite se face prin anulare și reemitere (dacă factura nu a ajuns la beneficiar) sau prin stornare urmată de factură nouă la valorile corecte (dacă a ajuns deja).
:::

## Cele două erori, separat

**Eroarea de perioadă.** Se folosește o cotă standard care a fost validă cândva, dar nu mai e validă la data facturii — de exemplu 19% pe o factură emisă după 01.08.2025, când cota standard a devenit 21%. E o eroare de dată, nu de produs: linia era, corect, la cotă standard — doar valoarea numerică a cotei standard s-a schimbat între timp.

**Eroarea de încadrare.** Se aplică 11% pe un produs care nu se regăsește pe lista limitativă de la art. 291 alin. (2) — sau invers, se aplică 21% pe un produs care de fapt e pe listă. E o eroare de clasificare a produsului, independentă de orice schimbare de dată.

Cele două se corectează la fel, prin art. 330 (stornare + factură nouă la cota corectă) — dar se **detectează** foarte diferit. O verificare automată care compară doar cota facturii cu cota standard valabilă la acea dată prinde prima categorie de erori, nu pe a doua: o factură cu 11% aplicat greșit unui serviciu care de fapt cerea 21% nu e o problemă de perioadă, e o problemă de clasificare de produs — și rămâne invizibilă pentru un instrument construit să verifice doar coerența de perioadă.

## Ce se greșește în practică

- Se tratează orice "cotă greșită" ca fiind aceeași problemă, și se aplică orbește aceeași verificare (de perioadă) pentru ambele cauze.
- Se citește un rezultat "totul e corect" al unei verificări de perioadă ca și cum ar confirma și clasificarea produsului — deși verificarea de perioadă nu se pronunță deloc asupra clasificării.
- Se corectează cota fără să se verifice dacă produsul se regăsește efectiv pe lista limitativă de la art. 291 alin. (2), înlocuind o presupunere cu alta.

## Ce face iConta.eu

Verificarea automată a cotei TVA pe facturile emise compară, linie cu linie, cota standard aplicată cu cota standard valabilă la data facturii — și se limitează explicit la liniile deja aflate la o cotă din familia standard (19% sau 21%). Liniile la cotă redusă sau scutit sunt lăsate deoparte, indiferent dacă încadrarea lor e corectă sau nu: verificarea **nu** stabilește dacă un produs trebuia să fie la cotă redusă sau la cotă standard — doar dacă valoarea cotei standard aplicate corespunde cu perioada facturii. Clasificarea produsului rămâne, integral, o decizie a contabilului, iar corectarea unei încadrări greșite se face manual, prin art. 330 — nu prin acest instrument.

[iConta.eu](/)
