---
title: Factura de marfă primită din Italia
description: Marfa cumpărată de la un furnizor din Italia e achiziție intracomunitară de bunuri (art. 268 alin. (3) lit. a) Cod fiscal), cu recepția fără TVA și taxa autoimpusă prin 4426 = 4427, nu prin plată la furnizor.
published: 2026-09-22
modified: 2026-09-22
poarta: v1
---

# Cum se înregistrează o factură de marfă primită din Italia?

O factură de la un furnizor italian pentru marfă de revânzare vine, ca regulă, fără TVA — furnizorul facturează pe baza codului tău de TVA valabil, comunicat lui înainte de livrare. Asta nu înseamnă că operațiunea scapă de TVA, ci că taxa se calculează la tine, cumpărătorul, prin taxare inversă, exact ca la orice altă achiziție de bunuri dintr-un stat membru UE.

## Temeiul legal

::: ghid-temei
**Art. 268 alin. (3) lit. a) Cod fiscal** — achiziția e AIC: *„Sunt, de asemenea, operațiuni impozabile și următoarele operațiuni efectuate cu plată, pentru care locul este considerat a fi în România, potrivit art. 276: a) o achiziție intracomunitară de bunuri, altele decât mijloace de transport noi sau produse accizabile, efectuată de o persoană impozabilă ce acționează ca atare sau de o persoană juridică neimpozabilă, care nu beneficiază de excepția prevăzută la alin. (4)..."*

**Art. 308 alin. (1) Cod fiscal** — obligația de plată e a cumpărătorului: *„Persoana care efectuează o achiziție intracomunitară de bunuri care este taxabilă, conform prezentului titlu, este obligată la plata taxei."*

**Norme HG 1/2016, pct. 109 alin. (1)** — formula contabilă: *„Din punct de vedere contabil, beneficiarul înregistrează în cursul perioadei fiscale în care taxa este exigibilă suma taxei aferente în următoarea formulă contabilă: 4426 = 4427. Prevederile acestui alineat sunt valabile pentru orice alte situații în care se aplică taxarea inversă."*
:::

## Conturi și formulă

Recepția mărfii se înregistrează la valoarea din factura furnizorului italian (convertită în lei), fără TVA:

`371 = 401` — marfă destinată revânzării.

TVA se autoimpune separat: `4426 = 4427`, cu `TVA = bază × cotă / 100`, rotunjit aritmetic la 2 zecimale.

Condiția de bază ca operațiunea să fie AIC e ca furnizorul să aibă un cod de TVA valabil dintr-un stat membru UE — în acest caz Italia (`IT`) — și ca marfa să provină efectiv dintr-un stat membru diferit de România. Nu contează dacă transportul e făcut de furnizor, de cumpărător sau de un terț în contul lor, atâta timp cât marfa ajunge fizic dintr-un stat membru în altul.

## Un exemplu

::: ghid-exemplu
O firmă cumpără marfă de la un furnizor din Italia, factură **12.500 lei**, cotă TVA **21%**.

- **Recepție marfă**: `371 = 401` cu **12.500 lei**
- **TVA autoimpusă**: `4426 = 4427` cu 12.500 × 21 / 100 = **2.625 lei**

Firma plătește furnizorului italian doar cei 12.500 lei ai facturii. TVA de 2.625 lei se evidențiază simultan la deduceri și la colectate în decontul lunii, fără plată suplimentară către nimeni.
:::

## Ce se greșește în practică

- **Se tratează factura ca „fără TVA" în sensul de scutire totală**, pentru că furnizorul italian n-a înscris nicio sumă de TVA — de fapt taxa există, doar că se autoimpune, nu se plătește furnizorului.
- **Se omite comunicarea codului de TVA propriu către furnizor înainte de livrare.** Fără el, furnizorul poate factura cu TVA italian, iar recuperarea acelei taxe devine un proces separat, mai greoi (cerere de rambursare din alt stat membru), nu o simplă corectare internă.
- **Se înregistrează doar marfa, fără taxarea inversă**, lăsând operațiunea contabilizată ca și cum n-ar avea nicio implicație de TVA în România.

## Ce face iConta.eu

Codul de TVA al furnizorului e analizat automat — prefixul de țară e verificat contra listei celor 27 de state membre UE plus `XI`; operațiunea e tratată ca intracomunitară doar dacă țara codului nu e România. TVA la taxare inversă se calculează cu `TVA = bază × cotă / 100`, rotunjit aritmetic (`ROUND_HALF_UP`) la 2 zecimale, cu cota transmisă explicit la fiecare calcul și baza strict pozitivă.

[iConta.eu](/)
