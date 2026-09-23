---
title: Factura către un client din UE se transmite în RO e-Factura?
description: Obligativitatea RO e-Factura vizează în principal relația B2B dintre firme stabilite în România. O factură către un client dintr-un alt stat membru UE nu intră, de regulă, sub această obligație - explicăm regula și excepțiile ei reale.
published: 2026-09-25
modified: 2026-09-25
poarta: v1
---

# Factura către un client din UE se transmite în RO e-Factura?

Răspunsul scurt, pentru majoritatea cazurilor: **nu**. Sistemul RO e-Factura a fost construit pentru relația dintre firme stabilite în România, nu pentru livrările intracomunitare către clienți din alte state membre. Există totuși o excepție de la excepție, pe care merită s-o cunoașteți dacă lucrați des cu parteneri din UE.

## Temeiul legal

::: ghid-temei
Prin excepție de la prevederile alin. (1), pentru operațiunile realizate între persoane impozabile stabilite în România conform art. 266 alin. (2), sunt considerate facturi numai facturile care îndeplinesc condițiile prevăzute de Ordonanța de urgență a Guvernului nr. 120/2021 privind administrarea, funcționarea și implementarea sistemului național privind factura electronică RO e-Factura și factura electronică în România [...]

— Codul fiscal (Legea 227/2015), art.319 alin.(1^1)
:::

::: ghid-temei
Sunt exceptate de la prevederile alin. (1)-(3): [...] b) livrările de bunuri/prestările de servicii efectuate către persoane impozabile care nu sunt stabilite și nici înregistrate în scopuri de TVA în România, conform art. 266 alin. (2) și, respectiv, art. 316 din Legea nr. 227/2015, cu modificările și completările ulterioare.

— Legea 296/2023, art. LIX alin.(4) lit.b) (obligativitatea RO e-Factura B2B)
:::

::: ghid-temei
Persoanele impozabile stabilite în România conform art. 266 alin. (2) din Legea nr. 227/2015 [...] au obligația pentru livrările de bunuri și prestările de servicii care au locul livrării/prestării în România [...] efectuate către persoane impozabile nestabilite, dar înregistrate în scopuri de TVA în România, să transmită facturile emise în sistemul național privind factura electronică RO e-Factura. Fac excepție [...] facturile emise pentru livrări intracomunitare de bunuri, pentru care beneficiarul comunică un cod de înregistrare în scopuri de TVA din alt stat membru.

— OUG 120/2021, art.10 alin.(1^1), introdus prin OUG 89/2025, art.X pct.1
:::

Regula de bază e simplă: obligativitatea RO e-Factura se aplică operațiunilor **dintre persoane impozabile stabilite în România** (art.319 alin.(1^1) CF). Un client dintr-un alt stat membru UE, care nu are sediul activității economice în România și nu e stabilit aici, cade practic mereu în afara acestei obligații — indiferent dacă operațiunea e o livrare intracomunitară de bunuri (scutită, cu cod de TVA valid al clientului) sau o prestare de servicii B2B cu locul la sediul beneficiarului.

Legea 296/2023 confirmă explicit acest lucru: sunt exceptate de la obligația RO e-Factura livrările/prestările către persoane impozabile "care nu sunt stabilite și nici înregistrate în scopuri de TVA în România". Un client obișnuit din UE, cu cod de TVA valid emis de statul lui membru, se încadrează exact aici.

Excepția de la excepție, adăugată recent prin OUG 89/2025: dacă furnizorul e stabilit în România și clientul, deși nu e stabilit aici, **este** înregistrat direct în scopuri de TVA în România (caz rar, dar posibil pentru operatori economici din UE cu înregistrare TVA românească directă), atunci factura trebuie transmisă prin RO e-Factura — *cu excepția* livrării intracomunitare de bunuri pentru care clientul comunică un cod de TVA valid dintr-un alt stat membru. Practic: cazul obișnuit (client UE cu TVA din țara lui) rămâne mereu în afara RO e-Factura.

## Ce se greșește în practică

- Se presupune că "orice factură emisă din România" trebuie transmisă prin RO e-Factura, indiferent de țara clientului — regula vizează relația dintre persoane stabilite în România, nu locul de emitere a facturii.
- Se confundă obligativitatea RO e-Factura cu obligațiile de facturare intracomunitară (cod TVA valid VIES, dovada transportului pentru scutirea de TVA) — sunt reguli separate, care se aplică amândouă, dar prima nu condiționează pe cealaltă.
- Se ignoră cazul rar, dar real, al clientului UE cu înregistrare TVA directă în România, pentru care obligația RO e-Factura poate reapărea.

## Ce face iConta.eu

Facturile către un client din UE se emit ca operațiuni intracomunitare (livrare de bunuri sau prestare de servicii B2B), cu validare a codului de TVA în VIES și verificarea condițiilor de scutire — separat de fluxul RO e-Factura. Transmiterea efectivă în SPV, prin conectorul OAuth cu ANAF, rămâne disponibilă pentru orice factură emisă, dar aplicația nu forțează și nu presupune că o factură către un client UE trebuie neapărat transmisă prin acest canal — decizia rămâne a contabilului, pe baza statutului real al clientului (stabilit/înregistrat TVA în România sau nu).

[iConta.eu](/)
