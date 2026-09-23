---
title: Cum deduc TVA aferentă achizițiilor intracomunitare
description: TVA la achiziția intracomunitară nu se plătește către furnizor și nu se deduce dintr-o factură primită cu TVA — se calculează prin taxare inversă, se înregistrează 4426 = 4427, iar deducerea e condiționată de aceleași reguli generale ca orice altă taxă deductibilă.
published: 2026-09-24
modified: 2026-09-24
poarta: v1
---

# Cum deduc TVA aferentă achizițiilor intracomunitare

La o achiziție intracomunitară de bunuri, furnizorul din alt stat membru nu facturează TVA — factura vine „netă”, fără taxă. Asta nu înseamnă că operațiunea e fără TVA în România: cumpărătorul, nu furnizorul, e cel obligat să calculeze și să înregistreze taxa, prin taxare inversă.

## Temeiul legal

::: ghid-temei
„Obligat la plata taxei = beneficiarul, la AIC/servicii primite.” — CF art. 308-309 (sursă: `cod_fiscal_227_2015_consolidat.txt`, L19405 și L19418, verificat în dosarul F050).
:::

Mecanic, taxarea inversă înseamnă că firma cumpărătoare calculează ea însăși TVA-ul aferent achiziției, îl înregistrează simultan ca taxă colectată și ca taxă deductibilă, iar norma de aplicare confirmă exact această formulă: „beneficiarul înregistrează… suma taxei aferente în următoarea formulă contabilă: 4426 = 4427” (HG 1/2016, norme la art. 331 pct. 109 alin. 1) — cu precizarea explicită că regula se aplică „pentru orice alte situații în care se aplică taxarea inversă”, deci și la achiziția intracomunitară.

## Ce înseamnă practic

Nu există o „factură cu TVA de dedus” de la furnizorul din UE — cota și baza de calcul le stabilești tu, cumpărătorul, pe baza facturii lui nete, la cota din România aplicabilă bunului respectiv. TVA-ul astfel calculat intră simultan în rândul de taxă colectată și în rândul de taxă deductibilă din decontul de TVA — dacă achiziția e destinată integral unor operațiuni cu drept de deducere, efectul net e zero, fără plată efectivă.

Data la care se face acest calcul (exigibilitatea) și cursul valutar folosit pentru conversie urmează reguli proprii, distincte de data facturii sau a plății — subiect tratat separat, în ghidul despre exigibilitatea TVA la achiziția intracomunitară.

## Ce se greșește în practică

Cea mai frecventă greșeală e așteptarea unei facturi „cu TVA de recuperat” de la furnizorul UE — nu vine, iar TVA-ul se calculează intern, prin autofactură dacă e cazul. A doua: aplicarea unei cote fixe „din obișnuință”, fără verificare la momentul operațiunii — cota de TVA aplicabilă bunului se poate schimba, iar o cotă scrisă rigid, fără reconfirmare, se dezactualizează tăcut la prima modificare legislativă. A treia: tratarea ca achiziție intracomunitară a unei operațiuni care de fapt intră sub art. 307 alin. (3)-(6) — o încadrare greșită care produce taxare inversă acolo unde nu se aplică.

## Ce face iConta.eu

Ecranul de achiziție intracomunitară cere valoarea în lei, codul de TVA al furnizorului, tipul operațiunii (bunuri/servicii) și cota de TVA aplicabilă — fără valoare implicită impusă de sistem, exact pentru ca o cotă „scrisă în cod” să nu se rupă tăcut de lege la prima schimbare. Motorul calculează taxa prin taxare inversă, cu rotunjire `Decimal` și `ROUND_HALF_UP`, și generează formula contabilă 4426 = 4427 cerută de normă. Obligația de plată rămâne, corect, a beneficiarului — furnizorul nu apare nicăieri ca plătitor al taxei românești.

[iConta.eu](/)
