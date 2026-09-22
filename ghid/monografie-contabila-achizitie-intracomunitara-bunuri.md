---
title: Monografia contabilă la o achiziție intracomunitară de bunuri
description: O achiziție de bunuri de la un furnizor din alt stat membru UE e operațiune impozabilă în România (art. 268 alin. (3) lit. a) Cod fiscal), iar TVA se autoimpune prin taxare inversă 4426 = 4427, conform pct. 109 alin. (1) din normele HG 1/2016.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Care este monografia contabilă pentru o achiziție intracomunitară de bunuri?

Când cumperi marfă sau materii prime de la un furnizor înregistrat în scop de TVA în alt stat membru UE, furnizorul îți facturează fără TVA, dar obligația de a calcula și evidenția taxa nu dispare — trece la tine, cumpărătorul. Mecanismul se numește taxare inversă: nu plătești TVA furnizorului, ci ți-o autoimpui prin două conturi care se egalează în aceeași lună. Greșeala tipică e fie ignorarea completă a TVA (tratezi factura ca și cum n-ar exista TVA românesc), fie așteptarea unei facturi cu TVA de la furnizor, care nu vine niciodată corect.

## Temeiul legal

::: ghid-temei
**Art. 268 alin. (3) lit. a) Cod fiscal** — AIC e operațiune impozabilă în România: *„Sunt, de asemenea, operațiuni impozabile și următoarele operațiuni efectuate cu plată, pentru care locul este considerat a fi în România, potrivit art. 276: a) o achiziție intracomunitară de bunuri, altele decât mijloace de transport noi sau produse accizabile, efectuată de o persoană impozabilă ce acționează ca atare sau de o persoană juridică neimpozabilă, care nu beneficiază de excepția prevăzută la alin. (4)..."*

**Art. 308 alin. (1) Cod fiscal** — cine datorează taxa: *„Persoana care efectuează o achiziție intracomunitară de bunuri care este taxabilă, conform prezentului titlu, este obligată la plata taxei."*

**Norme metodologice, HG 1/2016, pct. 109 alin. (1)** — formula contabilă: *„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă."*
:::

## Cele două înregistrări

O AIC generează două note contabile distincte, ambele în aceeași lună:

**1. Recepția mărfii/materialelor**, la valoarea din factura furnizorului (convertită în lei la cursul din data facturii sau a exigibilității, după caz):

`301/371/... = 401` — cu suma facturii externe, fără TVA (furnizorul nu facturează TVA).

**2. Autoimpunerea TVA prin taxare inversă**, calculată la baza de mai sus:

`4426 = 4427` — cu `TVA = bază × cotă / 100`, rotunjit la 2 zecimale.

Suma e simultan TVA deductibilă (4426) și TVA colectată (4427) — pentru o firmă cu drept integral de deducere, operațiunea e neutră în decontul de TVA (aceeași sumă apare și la deduceri, și la colectate), dar rămâne obligatorie de înregistrat și de raportat, inclusiv în D390 (declarația recapitulativă pentru achiziții intracomunitare).

**O excepție de reținut**: art. 268 alin. (4) scoate din sfera de impozitare în România achizițiile intracomunitare făcute de o persoană impozabilă care nu are drept de deducere sau de o persoană juridică neimpozabilă, dacă valoarea cumulată a acestor achiziții nu depășește plafonul de 10.000 euro pe an calendaristic (anul curent sau anterior). Regula vizează cumpărători fără drept de deducere sau neplătitori — pentru firma obișnuită, plătitoare de TVA cu regim normal, achizițiile intră direct sub art. 268 alin. (3) lit. a), fără plafon.

## Un exemplu

::: ghid-exemplu
O firmă cumpără materii prime de la un furnizor din Polonia, factură de **8.000 lei**, cotă TVA aplicabilă **21%**.

- **Recepție marfă**: `301 = 401` cu **8.000 lei**
- **TVA autoimpusă**: `4426 = 4427` cu 8.000 × 21 / 100 = **1.680 lei**

Firma nu plătește niciun leu de TVA suplimentar furnizorului — cei 8.000 lei ajung integral la el. TVA de 1.680 lei apare simultan la deduceri și la colectate în decontul lunii, iar operațiunea se raportează și în D390.
:::

## Ce se greșește în practică

- **Se așteaptă o factură cu TVA de la furnizorul UE.** Furnizorul facturează fără TVA, pe baza codului tău valabil de TVA; taxa se calculează la tine, nu la el.
- **Se înregistrează doar `301 = 401`, fără `4426 = 4427`.** Achiziția rămâne, contabil, „fără TVA" — greșit, pentru că obligația de autoimpunere există chiar dacă suma e neutră în decont.
- **Se aplică o cotă fixă, scrisă o dată în șablonul de notă contabilă.** Cota de TVA se poate schimba prin lege; o cotă înghețată în șablon rămâne validă doar până la prima modificare legislativă, apoi produce sume greșite tăcut.

## Ce face iConta.eu

Codul de TVA al furnizorului e analizat automat: prefixul de țară (cu excepția Greciei, mapată `GR → EL`, convenția folosită de VIES) e verificat contra listei celor 27 de state membre UE plus `XI` (Irlanda de Nord, regim special post-Brexit); dacă prefixul lipsește sau nu e recunoscut, operațiunea nu e tratată ca intracomunitară. O achiziție e considerată intracomunitară doar dacă țara codului de TVA nu e România.

Suma TVA la taxare inversă se calculează cu `TVA = bază × cotă / 100`, rotunjit aritmetic la 2 zecimale. Cota nu are valoare implicită — trebuie transmisă explicit la fiecare calcul, tocmai ca o schimbare de cotă prin lege să nu rămână „înghețată" într-o valoare veche scrisă cândva în cod.

[iConta.eu](/)
