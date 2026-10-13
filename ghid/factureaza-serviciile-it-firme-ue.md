---
title: "Cum se facturează serviciile IT către firme din UE?"
description: "Regula TVA pentru serviciile IT (dezvoltare software, consultanță, mentenanță) prestate unor firme din alte state membre UE."
published: 2026-09-26
modified: 2026-10-13
poarta: v1
---

# Cum se facturează serviciile IT către firme din UE?

Serviciile IT — dezvoltare software, consultanță, mentenanță, administrare de sisteme — prestate unei firme (persoană impozabilă) dintr-un alt stat membru UE urmează regula generală de TVA pentru servicii B2B, nu una specială pentru domeniul IT.

## Temeiul legal

::: ghid-temei
CF art. 278 alin. (2): „Locul prestării serviciilor B2B = locul beneficiarului (bază pentru neimpozabilitate în RO + declarare D390 cod S).” (sursă: Codul fiscal (Legea 227/2015), forma consolidată)
:::

Locul prestării unui serviciu B2B este locul unde este stabilit beneficiarul, nu locul unde e stabilit prestatorul. Practic: dacă firma client are un cod de TVA valid, verificat în VIES, într-un alt stat membru, serviciul IT nu se impozitează în România — se facturează fără TVA românesc, iar impozitarea revine statului beneficiarului, conform legislației lui. Nu contează dacă serviciul e livrat integral la distanță (dezvoltare, mentenanță remote) — regula e aceeași ca pentru orice altă prestare de servicii B2B.

Dacă beneficiarul nu are cod de TVA valid în VIES (de exemplu e persoană fizică sau firmă neînregistrată), operațiunea devine B2C: se facturează cu TVA românesc.

## Ce se greșește în practică

- Se presupune că „serviciile digitale” au un regim special, diferit de restul serviciilor B2B — nu e cazul aici; regula art. 278 alin. (2) e generală.
- Se emite factura fără TVA fără verificarea efectivă, în VIES, a codului de TVA al clientului la data facturii.
- Se omite declararea D390 (cod P), considerând eronat că o factură „fără TVA” nu mai are nicio obligație declarativă asociată.

## Ce face iConta.eu

Formularul de vânzare intracomunitară („vânzare intracomunitară (Operațiuni)”), categoria „Extern” a operațiunilor speciale, permite înregistrarea prestării de servicii către un client UE, cu câmp dedicat pentru codul de TVA al clientului. La emiterea facturii cu cod de TVA non-RO, sistemul verifică automat, live, în VIES starea codului și afișează rezultatul.

Pe baza acestor date, aplicația validează neimpozabilitatea în România — client non-RO + cod valid VIES — și clasifică operațiunea pentru D390 cod P (servicii prestate intracomunitar).

[iConta.eu](/)
